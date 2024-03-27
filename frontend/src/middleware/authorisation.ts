import { defineMiddleware } from "astro:middleware"
import { addMonths } from 'date-fns'
import * as jose from 'jose'
import { type AstroCookieSetOptions, type MiddlewareHandler } from 'astro'

import { refresh } from "@modules/api"
import { type Claims, RoleEnum } from "./authorisation.types"

export const accessTokenCookieName = "ACSS_TOKN_COOKIE",
    refreshTokenCookieName = "RFSH_TOKN_COOKIE",
    cookieOptions: AstroCookieSetOptions = { expires: addMonths(new Date(), 1), httpOnly: true, path: "/", sameSite: "strict", secure: true }

const extractClaims = (token: string): Claims => {
    return jose.decodeJwt(token)
}

const getCurrentTimeInSeconds = (): number => {
    return Math.floor(Date.now() / 1000)
}

export const onRequest: MiddlewareHandler = defineMiddleware(async (context, next) => {
    context.locals.claims = null
    context.locals.loggedIn = false
    context.locals.admin = false
    context.locals.name = null
    context.locals.token = null

    try {
        const accessToken = context.cookies.get(accessTokenCookieName)?.value ?? null,
            refreshToken = context.cookies.get(refreshTokenCookieName)?.value ?? null

        if (!accessToken) {            
            return next()
        }

        context.locals.token = accessToken

        // Just get the claims, we only do basic validation here as the backend handles security on the endpoints
        const claims = extractClaims(accessToken)

        if(!claims || Object.values(claims).length < 1) throw new Error("Token has no claims, skipping auth...")

        // Validate 'subject' claim, must be present
        if(!claims?.sub) throw new Error("Token has no subject, skipping auth...")

        // Validate 'not before' claim, if present
        if(claims?.nbf && claims.nbf > getCurrentTimeInSeconds()) throw new Error("Token not yet valid, skipping auth...")

        // Validate 'expiry' claim - necessary and required value
        // Refresh up to 30 seconds earlier than required, to account for any clock skew
        if(claims.exp - 30 < getCurrentTimeInSeconds()) {
            if(!refreshToken) throw new Error("Token has expired with no refresh token available, skipping auth...")

            try {
                const { access_token: newAccess, refresh_token: newRefresh } = await refresh(accessToken, refreshToken)

                context.cookies.set(accessTokenCookieName, newAccess, cookieOptions)
                context.cookies.set(refreshTokenCookieName, newRefresh, cookieOptions)

                context.locals.token = newAccess
            } catch(e) {
                // Token pair is no longer valid

                context.cookies.delete(accessTokenCookieName)
                context.cookies.delete(refreshTokenCookieName)

                return next()
            }
        }

        context.locals.claims = claims
        context.locals.loggedIn = true
        context.locals.admin = claims.role == RoleEnum.ADMIN
        context.locals.name = claims.name

        return next()
    } catch(e) {
        console.error(e)
        return next()
    }
});
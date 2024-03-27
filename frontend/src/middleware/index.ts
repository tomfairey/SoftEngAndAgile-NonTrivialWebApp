import { defineMiddleware } from "astro:middleware"

import { onRequest as authorisationOnRequest } from './authorisation'

export const onRequest = defineMiddleware((context, next) => {
    return authorisationOnRequest(context, next)
});

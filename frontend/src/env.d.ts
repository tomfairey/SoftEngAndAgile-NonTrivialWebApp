/// <reference types="astro/client" />

declare namespace App {
	interface Locals {
        claims: {} | null;
        loggedIn: boolean;
        admin: boolean;
        name: string | null;
		token: string | null;
	}
}

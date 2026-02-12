/**
 * Security utilities for SSPL-III compliance
 * Handles JWT authentication, nonce generation, and HMAC request signing
 */

// Types and Interfaces
export interface SignaturePayload {
    url: string
    method: string
    body?: string
    timestamp: number
    nonce: string
}

export interface SecureHeaders {
    'Authorization'?: string
    'X-Client-Nonce': string
    'X-Signature': string
    'X-Timestamp': string
}

/**
 * Get JWT token from environment or localStorage
 * @returns JWT token string or empty string if not available
 */
export function getJWT(): string {
    try {
        // Try environment variable first (for development/testing)
        const envToken = process.env.NEXT_PUBLIC_JWT_TOKEN
        if (envToken && envToken !== 'your_jwt_token_here') {
            return envToken
        }

        // Fallback to localStorage for dynamic login tokens
        if (typeof window !== 'undefined') {
            const storedToken = localStorage.getItem('jwt_token')
            if (storedToken) {
                return storedToken
            }
        }

        return ''
    } catch (error) {
        console.error('Error getting JWT token:', error)
        return ''
    }
}

/**
 * Generate a unique nonce for anti-replay protection
 * Format: {timestamp}-{uuid}
 * @returns Unique nonce string
 */
export function generateNonce(): string {
    try {
        const timestamp = Date.now()

        // Use crypto.randomUUID if available (modern browsers)
        if (typeof crypto !== 'undefined' && crypto.randomUUID) {
            const uuid = crypto.randomUUID()
            return `${timestamp}-${uuid}`
        }

        // Fallback: generate random string
        const randomStr = Math.random().toString(36).substring(2, 15) +
            Math.random().toString(36).substring(2, 15)
        return `${timestamp}-${randomStr}`
    } catch (error) {
        console.error('Error generating nonce:', error)
        // Ultimate fallback
        return `${Date.now()}-${Math.random().toString(36).substring(2)}`
    }
}

/**
 * Convert string to ArrayBuffer for Web Crypto API
 */
function stringToArrayBuffer(str: string): ArrayBuffer {
    const encoder = new TextEncoder()
    return encoder.encode(str).buffer
}

/**
 * Convert ArrayBuffer to hex string
 */
function arrayBufferToHex(buffer: ArrayBuffer): string {
    const byteArray = new Uint8Array(buffer)
    const hexCodes = Array.from(byteArray).map(byte => {
        const hex = byte.toString(16)
        return hex.padStart(2, '0')
    })
    return hexCodes.join('')
}

/**
 * Sign request using HMAC-SHA256
 * @param payload - Request details to sign
 * @returns Hex-encoded HMAC signature
 */
export async function signRequest(payload: SignaturePayload): Promise<string> {
    try {
        const secret = process.env.NEXT_PUBLIC_HMAC_SECRET || ''

        if (!secret || secret === 'your_hmac_secret_here') {
            // Suppress warning in production - only log once per session
            if (typeof window !== 'undefined' && !(window as any).__hmacWarningLogged) {
                console.debug('HMAC secret not configured, using empty signature (this is normal in development)')
                ;(window as any).__hmacWarningLogged = true
            }
            return ''
        }

        // Create canonical string: method|url|body|timestamp|nonce
        const canonicalString = [
            payload.method.toUpperCase(),
            payload.url,
            payload.body || '',
            payload.timestamp.toString(),
            payload.nonce
        ].join('|')

        // Check if Web Crypto API is available
        if (typeof crypto !== 'undefined' && crypto.subtle) {
            // Import the secret key
            const keyData = stringToArrayBuffer(secret)
            const key = await crypto.subtle.importKey(
                'raw',
                keyData,
                { name: 'HMAC', hash: 'SHA-256' },
                false,
                ['sign']
            )

            // Sign the canonical string
            const signature = await crypto.subtle.sign(
                'HMAC',
                key,
                stringToArrayBuffer(canonicalString)
            )

            return arrayBufferToHex(signature)
        } else {
            // Fallback: Use a simple hash (NOT cryptographically secure, for development only)
            console.warn('Web Crypto API not available, using fallback signature')

            // Simple hash function (FNV-1a)
            let hash = 2166136261
            for (let i = 0; i < canonicalString.length; i++) {
                hash ^= canonicalString.charCodeAt(i)
                hash += (hash << 1) + (hash << 4) + (hash << 7) + (hash << 8) + (hash << 24)
            }

            return (hash >>> 0).toString(16).padStart(8, '0')
        }
    } catch (error) {
        console.error('Error signing request:', error)
        return ''
    }
}

/**
 * Build complete set of security headers for a request
 * @param url - Request URL
 * @param method - HTTP method (GET, POST, etc.)
 * @param body - Request body (optional)
 * @returns Object containing all security headers
 */
export async function buildSecureHeaders(
    url: string,
    method: string,
    body?: any
): Promise<SecureHeaders> {
    try {
        // Generate nonce
        const nonce = generateNonce()

        // Get current timestamp
        const timestamp = Date.now()

        // Serialize body if present
        const bodyString = body ? JSON.stringify(body) : ''

        // Create signature payload
        const payload: SignaturePayload = {
            url,
            method,
            body: bodyString,
            timestamp,
            nonce
        }

        // Generate signature
        const signature = await signRequest(payload)

        // Build headers object
        const headers: SecureHeaders = {
            'X-Client-Nonce': nonce,
            'X-Signature': signature,
            'X-Timestamp': timestamp.toString()
        }

        // Add JWT if available
        const jwt = getJWT()
        if (jwt) {
            headers['Authorization'] = `Bearer ${jwt}`
        }

        return headers
    } catch (error) {
        console.error('Error building secure headers:', error)

        // Return minimal headers on error
        return {
            'X-Client-Nonce': generateNonce(),
            'X-Signature': '',
            'X-Timestamp': Date.now().toString()
        }
    }
}

/**
 * Check if an error is an authentication error (401/403)
 * @param error - Error object or HTTP response
 * @returns true if authentication error
 */
export function isAuthError(error: any): boolean {
    if (error?.status === 401 || error?.status === 403) {
        return true
    }
    if (error?.response?.status === 401 || error?.response?.status === 403) {
        return true
    }
    return false
}

/**
 * Custom authentication error class
 */
export class AuthenticationError extends Error {
    status: number

    constructor(message: string, status: number = 401) {
        super(message)
        this.name = 'AuthenticationError'
        this.status = status
    }
}

/**
 * Store JWT token in localStorage
 * @param token - JWT token string
 */
export function setJWT(token: string): void {
    try {
        if (typeof window !== 'undefined') {
            localStorage.setItem('jwt_token', token)
        }
    } catch (error) {
        console.error('Error storing JWT token:', error)
    }
}

/**
 * Clear JWT token from localStorage
 */
export function clearJWT(): void {
    try {
        if (typeof window !== 'undefined') {
            localStorage.removeItem('jwt_token')
        }
    } catch (error) {
        console.error('Error clearing JWT token:', error)
    }
}

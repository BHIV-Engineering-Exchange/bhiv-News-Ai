// Email service utility
// In production, you would use a real email service like SendGrid, AWS SES, or Resend

export interface EmailData {
  to: string
  subject: string
  html: string
}

// Mock email sending for development
// Replace this with your actual email service integration
export async function sendEmail(data: EmailData): Promise<boolean> {
  // For now, just log the email to console
  console.log('📧 Email would be sent:', {
    to: data.to,
    subject: data.subject,
    // Don't log full HTML in production
    htmlLength: data.html.length
  })
  
  // Return true to simulate successful sending
  // In production, replace with actual email service
  return true
}

export function generateVerificationEmail(userName: string, verificationLink: string): string {
  return `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Verify Your Email</title>
      <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #8B5CF6, #EC4899); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
        .button { display: inline-block; background: linear-gradient(135deg, #8B5CF6, #EC4899); color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; margin: 20px 0; }
        .footer { text-align: center; color: #666; font-size: 12px; margin-top: 30px; }
      </style>
    </head>
    <body>
      <div class="header">
        <h1>Welcome to Blackhole Infiverse!</h1>
      </div>
      <div class="content">
        <h2>Hi ${userName},</h2>
        <p>Thank you for signing up! Please verify your email address by clicking the button below:</p>
        <div style="text-align: center;">
          <a href="${verificationLink}" class="button">Verify Email</a>
        </div>
        <p>Or copy and paste this link into your browser:</p>
        <p style="word-break: break-all; color: #8B5CF6;">${verificationLink}</p>
        <p><strong>Note:</strong> This link will expire in 24 hours.</p>
      </div>
      <div class="footer">
        <p>Blackhole Infiverse LLP - Advanced AI News Analysis</p>
        <p>If you didn't create an account, you can safely ignore this email.</p>
      </div>
    </body>
    </html>
  `
}

export function generatePasswordResetEmail(userName: string, resetLink: string): string {
  return `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Reset Your Password</title>
      <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #8B5CF6, #EC4899); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
        .button { display: inline-block; background: linear-gradient(135deg, #8B5CF6, #EC4899); color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; margin: 20px 0; }
        .footer { text-align: center; color: #666; font-size: 12px; margin-top: 30px; }
        .warning { background: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 5px; margin: 20px 0; }
      </style>
    </head>
    <body>
      <div class="header">
        <h1>Password Reset Request</h1>
      </div>
      <div class="content">
        <h2>Hi ${userName},</h2>
        <p>We received a request to reset your password. Click the button below to create a new password:</p>
        <div style="text-align: center;">
          <a href="${resetLink}" class="button">Reset Password</a>
        </div>
        <p>Or copy and paste this link into your browser:</p>
        <p style="word-break: break-all; color: #8B5CF6;">${resetLink}</p>
        <div class="warning">
          <strong>⚠️ Important:</strong> This link will expire in 1 hour for security reasons.
        </div>
      </div>
      <div class="footer">
        <p>Blackhole Infiverse LLP - Advanced AI News Analysis</p>
        <p>If you didn't request a password reset, please ignore this email or contact support if you're concerned.</p>
      </div>
    </body>
    </html>
  `
}

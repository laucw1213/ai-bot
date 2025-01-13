// pages/api/webhook.js
import crypto from 'crypto';

// Verify GitHub webhook signature
const verifySignature = (req) => {
  const signature = req.headers['x-hub-signature-256'];
  if (!signature) return false;

  const secret = process.env.WEBHOOK_SECRET;
  const body = JSON.stringify(req.body);
  const hmac = crypto.createHmac('sha256', secret);
  const digest = 'sha256=' + hmac.update(body).digest('hex');
  return crypto.timingSafeEqual(Buffer.from(signature), Buffer.from(digest));
};

export default async function handler(req, res) {
  // Only accept POST requests
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  // Verify webhook signature
  if (!verifySignature(req)) {
    return res.status(401).json({ error: 'Invalid signature' });
  }

  try {
    // Extract information from the webhook payload
    const { repository, after: commitSha } = req.body;
    console.log(`Received webhook for ${repository.full_name}, commit: ${commitSha}`);

    // Trigger GitHub Action in ai-bot repository
    const response = await fetch(
      'https://api.github.com/repos/laucw1213/ai-bot/dispatches',
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${process.env.GITHUB_TOKEN}`,
          'Accept': 'application/vnd.github.v3+json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          event_type: 'super_interview_update',
          client_payload: {
            repository: repository.full_name,
            commit: commitSha
          }
        })
      }
    );

    if (!response.ok) {
      console.error('Failed to trigger workflow:', await response.text());
      return res.status(500).json({ error: 'Failed to trigger workflow' });
    }

    res.status(200).json({ 
      message: 'Webhook processed successfully',
      triggered: 'super_interview_update'
    });

  } catch (error) {
    console.error('Error processing webhook:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
}
// pages/api/webhook.js
export default async function handler(req, res) {
    // Log every request immediately
    console.log('Webhook received:', {
      method: req.method,
      path: req.url,
      headers: req.headers,
      body: req.body
    });
  
    try {
      // Only accept POST requests
      if (req.method !== 'POST') {
        console.log('Invalid method:', req.method);
        return res.status(405).json({ error: 'Method not allowed' });
      }
  
      const eventType = req.headers['x-github-event'];
      console.log('GitHub Event:', eventType);
  
      // For now, accept all requests for testing
      // We'll add signature verification back later
      const response = await fetch(
        'https://api.github.com/repos/laucw1213/ai-bot/dispatches',
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${process.env.GITHUB_TOKEN}`,
            'Accept': 'application/vnd.github+json',
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            event_type: 'mctest_update',
            client_payload: {
              repository: req.body.repository?.full_name || 'unknown',
              commit: req.body.after || 'unknown'
            }
          })
        }
      );
  
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Failed to trigger workflow:', errorText);
        return res.status(500).json({ 
          error: 'Failed to trigger workflow', 
          details: errorText 
        });
      }
  
      console.log('Workflow triggered successfully');
      return res.status(200).json({ 
        message: 'Success',
        event: eventType,
        triggered: 'mctest_update'
      });
  
    } catch (error) {
      console.error('Webhook error:', error);
      return res.status(500).json({ 
        error: 'Internal server error',
        message: error.message
      });
    }
  }

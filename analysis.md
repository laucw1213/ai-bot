# Super Interview Repository Analysis
Generated at: 2025-01-13 08:46:43 UTC

## Repository Structure
```
 |--suggestAnswers.gs
 |--webapp.gs
 |--README.md
 |--createForm.gs
 |--prefilledLink.gs
 |--makePublic.gs
 |--index.html
 |--test.gs
 |--findEntryIds.gs
 |--LICENSE
 |--findQuestions.gs
 |--finddoc.gs
 |--createSheel.gs
 |--config.gs
 |--Code.gs
```

## File Contents
### ./suggestAnswers.gs
```
function suggestAnswers(questions) {
  try {
    // Get API key from project properties
    const apiKey = PropertiesService.getScriptProperties().getProperty('GEMINI_API_KEY');
    if (!apiKey) {
      throw new Error('Gemini API key not found in script properties');
    }

    // Format prompt to request JSON response with realistic info
    const prompt = `Act as an expert sales professional and generate interview responses.

For a more natural response, provide your response in this exact format (do not include any code blocks or backticks):
{
  "responses": [
    "Your name (realistic)",
    "Your Hong Kong mobile number (+852 format)",
    "Your email address (matching the name)",
    "detailed answer to fourth question",
    "detailed answer to fifth question",
    "etc..."
  ]
}

Guidelines for answers after the first three:
- Demonstrate strong negotiation skills and empathy
- Include specific examples with metrics
- Keep responses professional and concise (150-200 words)
- Focus on showing skills and experience
- Do not include the question text
- Align answers with the questions asked

Here are the questions:
${questions.map((q, i) => `${i + 1}. ${q}`).join('\n')}`;

    // Call Gemini API
    const response = callGeminiAPI(prompt, apiKey);
    Logger.log('Raw API response:', response);
    
    // Handle response parsing
    let parsedResponse;
    try {
      // Clean up the response text
      let cleanedResponse = response;
      
      // If response is wrapped in code blocks, extract it
      const codeBlockMatch = response.match(/```(?:json)?\s*([\s\S]+?)\s*```/);
      if (codeBlockMatch) {
        cleanedResponse = codeBlockMatch[1];
      }

      // Ensure the response has proper JSON structure
      if (!cleanedResponse.trim().startsWith('{')) {
        cleanedResponse = '{' + cleanedResponse;
      }
      if (!cleanedResponse.trim().endsWith('}')) {
        cleanedResponse = cleanedResponse + '}';
      }

      Logger.log('Cleaned response:', cleanedResponse);
      parsedResponse = JSON.parse(cleanedResponse);
      
    } catch (parseError) {
      Logger.log('Parse error:', parseError);
      throw new Error(`Failed to parse API response: ${parseError.message}`);
    }

    // Extract answers from parsed response
    const answers = parsedResponse.responses || [];
    Logger.log('Parsed answers:', answers);

    // Ensure we have enough answers
    const resultAnswers = new Array(questions.length).fill('No answer generated');
    answers.forEach((answer, index) => {
      if (index < questions.length) {
        resultAnswers[index] = answer;
      }
    });

    return {
      questions: questions,
      answers: resultAnswers
    };

  } catch (error) {
    Logger.log(`Error in suggestAnswers: ${error.message}`);
    // Return more informative error messages instead of generic ones
    return {
      questions: questions,
      answers: new Array(questions.length).fill(`Error: ${error.message}`)
    };
  }
}

function callGeminiAPI(prompt, apiKey) {
  // Updated endpoint for Gemini 1.5 Pro
  const apiEndpoint = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key=${apiKey}`;
  
  const requestBody = {
    contents: [{
      parts: [{
        text: prompt
      }]
    }],
    generationConfig: {
      temperature: 0.7,
      topK: 40,
      topP: 0.95,
      maxOutputTokens: 2048,
      candidateCount: 1
    },
    safetySettings: [
      {
        category: "HARM_CATEGORY_HARASSMENT",
        threshold: "BLOCK_MEDIUM_AND_ABOVE"
      },
      {
        category: "HARM_CATEGORY_HATE_SPEECH",
        threshold: "BLOCK_MEDIUM_AND_ABOVE"
      }
    ]
  };

  const options = {
    method: 'post',
    headers: {
      'Content-Type': 'application/json'
    },
    payload: JSON.stringify(requestBody),
    muteHttpExceptions: true
  };

  try {
    const response = UrlFetchApp.fetch(apiEndpoint, options);
    const responseCode = response.getResponseCode();
    
    Logger.log(`API Response Code: ${responseCode}`);
    
    if (responseCode !== 200) {
      Logger.log(`API Response: ${response.getContentText()}`);
      throw new Error(`API request failed with status ${responseCode}: ${response.getContentText()}`);
    }
    
    const responseData = JSON.parse(response.getContentText());
    Logger.log('API Response Data:', JSON.stringify(responseData, null, 2));
    
    if (!responseData.candidates || responseData.candidates.length === 0) {
      throw new Error('No response generated from Gemini');
    }
    
    // Extract text from response
    const rawText = responseData.candidates[0].content.parts[0].text;
    
    // Clean the response text to handle code blocks
    let cleanedText = rawText;
    
    // Remove code block markers if present
    const codeBlockMatch = rawText.match(/```(?:json)?\s*([\s\S]+?)\s*```/);
    if (codeBlockMatch) {
      cleanedText = codeBlockMatch[1];
    }
    
    // Remove any leading/trailing whitespace and standalone curly braces
    cleanedText = cleanedText.trim().replace(/^{/, '').replace(/}$/, '');
    
    Logger.log('Cleaned response text:', cleanedText);
    return cleanedText;
    
  } catch (error) {
    Logger.log(`Error calling Gemini API: ${error.message}`);
    throw error;
  }
}

function parseJsonResponse(response, expectedAnswerCount) {
  try {
    Logger.log('Raw response:', response);

    // Try to find JSON in the response
    let jsonStr = response;
    
    // If response is wrapped in code blocks, extract it
    const jsonMatch = response.match(/```(?:json)?\s*({[\s\S]+?})\s*```/);
    if (jsonMatch) {
      jsonStr = jsonMatch[1];
    }

    // Clean up any potential leading/trailing content
    jsonStr = jsonStr.replace(/^[^{]*/, '').replace(/[^}]*$/, '');
    
    Logger.log('Cleaned JSON string:', jsonStr);

    // Parse the JSON
    const parsed = JSON.parse(jsonStr);
    Logger.log('Parsed JSON:', JSON.stringify(parsed, null, 2));
    
    // Extract all responses
    const responses = parsed.responses || [];
    Logger.log('Parsed responses count:', responses.length);

    // Ensure we have exactly the number of answers we need
    const resultAnswers = new Array(expectedAnswerCount).fill('No answer generated');
    responses.forEach((answer, index) => {
      if (index < expectedAnswerCount) {
        resultAnswers[index] = answer;
      }
    });

    Logger.log('Final processed answers:', resultAnswers.length);
    return resultAnswers;
  } catch (error) {
    Logger.log(`Error parsing JSON response: ${error.message}`);
    Logger.log('Raw response:', response);
    return new Array(expectedAnswerCount).fill('Error generating answer');
  }
}```

### ./webapp.gs
```
function doGet() {
  return HtmlService.createHtmlOutputFromFile('index')
    .setTitle('Google Doc Form Generator')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

function processGoogleDoc(docId, aspects) {
  try {
    PropertiesService.getScriptProperties().setProperty('QUESTIONS_DOC_ID', docId);
    CONFIG.QUESTIONS_DOC_ID = docId;
    
    const params = {
      aspects: aspects
    };
    
    const result = main(params);
    
    // 检查执行结果
    if (result.status === 'error') {
      return {
        error: result.error
      };
    }
    
    return {
      sheetUrl: getSheetUrl(result.sheetId),
      formId: result.formId,
      prefilledUrl: result.prefilledUrl
    };
    
  } catch (error) {
    Logger.log('Process error: ' + error.toString());
    return {
      error: error.message || '处理失败'
    };
  }
}

function getSheetUrl(sheetId) {
  try {
    const sheet = SpreadsheetApp.openById(sheetId);
    return sheet.getUrl();
  } catch (error) {
    Logger.log(`Error getting sheet URL: ${error.message}`);
    throw error;
  }
}

function getFormEditorUrl(formId) {
  try {
    const form = FormApp.openById(formId);
    return form.getEditUrl();
  } catch (error) {
    throw new Error('Unable to generate form editor URL');
  }
}

function getPublishedFormUrl(formId) {
  try {
    const form = FormApp.openById(formId);
    return form.getPublishedUrl();
  } catch (error) {
    throw new Error('Unable to get published form URL');
  }
}```

### ./README.md
```
# test

这是一个测试项目。1213
```

### ./createForm.gs
```
function createFormInFolder(sheetId) {
  try {
    // Get configuration from project settings
    const config = getConfig();
    
    // Get target folder
    const targetFolder = DriveApp.getFolderById(config.TARGET_FOLDER_ID);
    
    // Get the source document name
    const sourceDoc = DocumentApp.openById(config.QUESTIONS_DOC_ID);
    const sourceName = sourceDoc.getName();
    const timestamp = getTimestampSuffix();
    const formTitle = `${sourceName} - Form (${timestamp})`;
    
    // Create form directly in target folder
    const form = FormApp.create(formTitle);
    const formId = form.getId();
    const formFile = DriveApp.getFileById(formId);
    
    // Move to target folder and remove from root
    targetFolder.addFile(formFile);
    DriveApp.getRootFolder().removeFile(formFile);
    Logger.log(`Created form in target folder: ${formId} with name: ${formTitle}`);

    // Add questions to form using stored questionsData
    if (questionsData && questionsData.length > 0) {
      questionsData.forEach(question => {
        if (question.trim()) {
          form.addParagraphTextItem().setTitle(question).setRequired(true);
        }
      });
    }

    // Set form destination
    form.setDestination(FormApp.DestinationType.SPREADSHEET, sheetId);
    Logger.log(`Form linked to spreadsheet: ${sheetId}`);

    return formId;
  } catch (error) {
    Logger.log(`Error in createFormInFolder: ${error.message}`);
    throw error;
  }
}```

### ./prefilledLink.gs
```
function generatePrefilledLink(formUrl, entryIds, answers) {
  try {
    // Validate inputs
    if (!entryIds || !answers) {
      throw new Error('Missing entry IDs or answers');
    }

    // Get base URL - remove any existing parameters
    const baseUrl = formUrl.split('?')[0];
    
    // Create prefilled parameters by combining entry IDs with answers
    const prefilledParams = entryIds
      .map((id, index) => `${id}=${encodeURIComponent(answers[index])}`)
      .join('&');
    
    // Generate the final prefilled URL
    const prefilledUrl = `${baseUrl}?usp=pp_url&${prefilledParams}`;
    
    Logger.log('Generated prefilled URL:');
    Logger.log(prefilledUrl);
    
    return prefilledUrl;
    
  } catch (error) {
    Logger.log(`Error generating prefilled link: ${error.message}`);
    throw error;
  }
}```

### ./makePublic.gs
```

// === makeFormPublic.gs ===
function makeFormPublic(formId) {
  try {
    const form = FormApp.openById(formId);
    form.setRequireLogin(false);
    Logger.log(`Form with ID ${formId} is now public.`);
  } catch (error) {
    Logger.log(`Error making form public: ${error.message}`);
    throw error;
  }
}
```

### ./index.html
```
<!DOCTYPE html>
<html>
<head>
    <title>Google Doc Form Generator</title>
    <style>
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            font-family: Arial, sans-serif;
        }

        .input-url, .aspect-input {
            width: 100%;
            padding: 8px;
            margin-top: 10px;
            margin-bottom: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            background-color: white;
        }

        .generate-button:disabled {
            background-color: #cccccc;
            cursor: not-allowed;
        }

        .guide-text {
            font-size: 14px;
            color: #666;
            margin: 10px 0;
        }    

        .input-section {
            margin-bottom: 20px;
        }

        .loading-spinner {
            display: none;
            color: #666;
        }

        .error {
            color: red;
            display: none;
            margin: 10px 0;
        }

        .result {
            display: none;
        }

        .step {
            margin-bottom: 20px;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 5px;
            display: none;
        }

        .step.completed {
            background-color: #f8f9fa;
            opacity: 0.8;
        }

        .step.completed .action-button {
            display: none !important;
        }

        .step.completed .step-header::before {
            content: "✓ ";
            color: #34a853;
        }

        .step.active {
            display: block;
            border: 2px solid #4285f4;
        }

        .step.visible {
            display: block;
        }

        .step-header {
            font-weight: bold;
            margin-bottom: 10px;
        }

        .link-container {
            margin-bottom: 20px;
            padding: 15px;
            background-color: #f5f5f5;
            border-radius: 5px;
        }

        .link-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 10px;
        }

        .link-title {
            font-weight: bold;
        }

        .action-button {
            background-color: #4285f4;
            color: white;
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            text-decoration: none;
            margin-left: 10px;
        }

        .action-button:hover {
            background-color: #357abd;
        }

        .action-button.open-button {
            background-color: #4285f4;
        }

        .action-button.confirm-button {
            background-color: #34a853;
            display: none;
        }

        .generate-button {
            background-color: #4285f4;
            color: white;
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }

        .generate-button:hover {
            background-color: #357abd;
        }

        .completion-message {
            text-align: center;
            padding: 20px;
            background-color: #e6f4ea;
            border-radius: 5px;
            margin-top: 20px;
            display: none;
        }

        .completion-message h2 {
            color: #34a853;
            margin-bottom: 10px;
        }

        .form-url-container {
            margin-top: 15px;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 4px;
        }

        .form-url {
            word-break: break-all;
            font-family: monospace;
            color: #1a73e8;
            padding: 10px;
            margin: 10px 0;
            background-color: white;
            border-radius: 4px;
            border: 1px solid #ddd;
        }

        .copy-button {
            margin-top: 10px;
            background-color: #4285f4;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
        }

        .copy-button:hover {
            background-color: #357abd;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 style="display: flex; align-items: center; gap: 10px;">
            <svg width="32" height="32" viewBox="0 0 52 52">
                <rect fill="none" height="4.8" rx="1.6" width="27.2" x="12.4" y="26"/>
                <rect fill="none" height="4.8" rx="1.6" width="24" x="12.4" y="35.6"/>
                <g>
                    <path d="m36.4 14.8h8.48a1.09 1.09 0 0 0 1.12-1.12 1 1 0 0 0 -.32-.8l-10.56-10.56a1 1 0 0 0 -.8-.32 1.09 1.09 0 0 0 -1.12 1.12v8.48a3.21 3.21 0 0 0 3.2 3.2z" fill="currentColor"/>
                    <path d="m44.4 19.6h-11.2a4.81 4.81 0 0 1 -4.8-4.8v-11.2a1.6 1.6 0 0 0 -1.6-1.6h-16a4.81 4.81 0 0 0 -4.8 4.8v38.4a4.81 4.81 0 0 0 4.8 4.8h30.4a4.81 4.81 0 0 0 4.8-4.8v-24a1.6 1.6 0 0 0 -1.6-1.6zm-32-1.6a1.62 1.62 0 0 1 1.6-1.55h6.55a1.56 1.56 0 0 1 1.57 1.55v1.59a1.63 1.63 0 0 1 -1.59 1.58h-6.53a1.55 1.55 0 0 1 -1.58-1.58zm24 20.77a1.6 1.6 0 0 1 -1.6 1.6h-20.8a1.6 1.6 0 0 1 -1.6-1.6v-1.57a1.6 1.6 0 0 1 1.6-1.6h20.8a1.6 1.6 0 0 1 1.6 1.6zm3.2-9.6a1.6 1.6 0 0 1 -1.6 1.63h-24a1.6 1.6 0 0 1 -1.6-1.6v-1.6a1.6 1.6 0 0 1 1.6-1.6h24a1.6 1.6 0 0 1 1.6 1.6z" fill="currentColor"/>
                </g>
            </svg>
            Interview Form Bot
        </h1>

        <div class="input-section">
            <div class="step-header">Step 1: Select Question Document and Enter Aspects</div>
            <select id="docSelector" class="input-url">
                <option value="">Select a document...</option>
            </select>
            
            <input 
                type="text" 
                id="aspectInput" 
                class="aspect-input" 
                placeholder="Enter aspects (comma-separated, e.g.: Technical, Communication, Leadership)"
            />
            
            <div class="guide-text">
                Available documents will be loaded from your project folder.<br>
                Enter aspects separated by commas that you want to evaluate.
            </div>
            
            <button id="generateButton" onclick="generateForm()" class="generate-button" disabled>
                Generate Form
            </button>
            <div id="loadingSpinner" class="loading-spinner">Generating...</div>
        </div>

        <div id="error" class="error"></div>

        <div id="result" class="result">
            <!-- Step 2: Form Editor -->
            <div id="step2" class="step">
                <div class="step-header">Step 2: Review and Confirm Form</div>
                <div class="link-container">
                    <div class="link-header">
                        <span class="link-title">Instructions:</span>
                        <div>
                            <button id="formEditorOpen" class="action-button open-button" onclick="handleFormEditorOpen()">Open Form</button>
                            <button id="formEditorConfirm" class="action-button confirm-button" onclick="confirmStep(2)">Confirm</button>
                        </div>
                    </div>
                    <div class="guide-text">
                        1. Open the form editor to review the questions<br>
                        2. Make any necessary adjustments<br>
                        3. Click Confirm when ready
                    </div>
                </div>
            </div>

            <!-- Step 3: Response Sheet -->
            <div id="step3" class="step">
                <div class="step-header">Step 3: Response Sheet Setup</div>
                <div class="link-container">
                    <div class="link-header">
                        <span class="link-title">Instructions:</span>
                        <div>
                            <button id="sheetOpen" class="action-button open-button" onclick="handleSheetOpen()">Open Sheet</button>
                            <button id="sheetConfirm" class="action-button confirm-button" onclick="confirmStep(3)">Confirm</button>
                        </div>
                    </div>
                    <div class="guide-text">
                        1. Open the response sheet<br>
                        2. Wait for 30 seconds until "Form Tools" show on menu.<br>
                        3. Click "Form Tools" next to "Help" menu on the top<br>
                        4. Select "Setup Form Trigger"<br>
                        5. Complete the authorization process<br>
                        6. Click Confirm after setup is complete
                    </div>
                </div>
            </div>

            <!-- Step 4: Prefilled Form -->
            <div id="step4" class="step">
                <div class="step-header">Step 4: Test Submission</div>
                <div class="link-container">
                    <div class="link-header">
                        <span class="link-title">Instructions:</span>
                        <div>
                            <button id="prefilledFormOpen" class="action-button open-button" onclick="handlePrefilledFormOpen()">Open Form</button>
                            <button id="prefilledFormConfirm" class="action-button confirm-button" onclick="confirmStep(4)">Confirm</button>
                        </div>
                    </div>
                    <div class="guide-text">
                        1. Open the pre-filled form<br>
                        2. Review all answers<br>
                        3. Scroll to bottom and submit the form
                    </div>
                </div>
            </div>

            <!-- Step 5: Gmail -->
            <div id="step5" class="step">
                <div class="step-header">Step 5: Send Interview Email</div>
                <div class="link-container">
                    <div class="link-header">
                        <span class="link-title">Instructions:</span>
                        <div>
                            <button id="gmailOpen" class="action-button open-button" onclick="handleGmailOpen()">Open Gmail</button>
                            <button id="gmailConfirm" class="action-button confirm-button" onclick="showCompletion()">Confirm</button>
                        </div>
                    </div>
                    <div class="guide-text">
                        1. Open Gmail<br>
                        2. Create new email for sending the form<br>
                        3. Click Confirm after sending the email
                    </div>
                </div>
            </div>

            <!-- Completion Message -->
            <div id="completionMessage" class="completion-message">
                <h2>Congratulations!</h2>
                <p>Your form is ready to distribute</p>
                <div class="form-url-container">
                    <p>Form URL:</p>
                    <div id="formUrl" class="form-url"></div>
                    <button onclick="copyFormUrl()" class="copy-button">Copy URL</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        let formData = {};

        function generateForm() {
            const docId = document.getElementById('docSelector').value;
            const aspects = document.getElementById('aspectInput').value;
            
            if (!docId) {
                showError('Please select a document');
                return;
            }
            
            if (!aspects.trim()) {
                showError('Please enter at least one aspect');
                return;
            }

            document.getElementById('generateButton').style.display = 'none';
            document.getElementById('loadingSpinner').style.display = 'block';
            document.getElementById('error').style.display = 'none';

            google.script.run
                .withSuccessHandler(updateUI)
                .withFailureHandler(handleError)
                .processGoogleDoc(docId, aspects);
        }

        function handleError(error) {
            showError(error);
            document.getElementById('generateButton').style.display = 'block';
            document.getElementById('loadingSpinner').style.display = 'none';
        }

        function handleFormEditorOpen() {
            if (formData.formId) {
                google.script.run
                    .withSuccessHandler(function(url) {
                        window.open(url, '_blank');
                        document.getElementById('formEditorOpen').style.display = 'none';
                        document.getElementById('formEditorConfirm').style.display = 'inline-block';
                    })
                    .withFailureHandler(function(error) {
                        showError('Could not open form editor: ' + error);
                    })
                    .getFormEditorUrl(formData.formId);
            }
        }

        function handleSheetOpen() {
            if (formData.sheetUrl) {
                window.open(formData.sheetUrl, '_blank');
                document.getElementById('sheetOpen').style.display = 'none';
                document.getElementById('sheetConfirm').style.display = 'inline-block';
            }
        }

        function handlePrefilledFormOpen() {
            if (formData.prefilledUrl) {
                window.open(formData.prefilledUrl, '_blank');
                document.getElementById('prefilledFormOpen').style.display = 'none';
                document.getElementById('prefilledFormConfirm').style.display = 'inline-block';
            }
        }

        function handleGmailOpen() {
            window.open('https://mail.google.com', '_blank');
            document.getElementById('gmailOpen').style.display = 'none';
            document.getElementById('gmailConfirm').style.display = 'inline-block';
        }

        function updateUI(result) {
            document.getElementById('loadingSpinner').style.display = 'none';
            
            if (result.error) {
                showError(result.error);
                document.getElementById('generateButton').style.display = 'block';
                return;
            }
            
            formData = result;
            document.getElementById('result').style.display = 'block';
            const step2 = document.getElementById('step2');
            step2.classList.add('visible', 'active');
        }

        function showError(error) {
            document.getElementById('loadingSpinner').style.display = 'none';
            const errorDiv = document.getElementById('error');
            errorDiv.textContent = 'Error: ' + error;
            errorDiv.style.display = 'block';
        }

        function confirmStep(stepNum) {
            // Mark current step as completed
            const currentStep = document.getElementById(`step${stepNum}`);
            currentStep.classList.add('completed');
            currentStep.classList.remove('active');
            
            if (stepNum < 5) {
                // Show and activate next step
                const nextStep = document.getElementById(`step${stepNum + 1}`);
                nextStep.classList.add('visible', 'active');
                
                // Reset the buttons state for the next step
                if (nextStep) {
                    const openButton = nextStep.querySelector('.open-button');
                    const confirmButton = nextStep.querySelector('.confirm-button');
                    if (openButton) openButton.style.display = 'inline-block';
                    if (confirmButton) confirmButton.style.display = 'none';
                }
                
                // Scroll to the next step smoothly
                nextStep.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }

        function showCompletion() {
            // Mark step 5 as completed
            const step5 = document.getElementById('step5');
            step5.classList.add('completed');
            step5.classList.remove('active');
            
            // Get form URL and show completion message
            google.script.run
                .withSuccessHandler(function(url) {
                    document.getElementById('formUrl').textContent = url;
                    document.getElementById('completionMessage').style.display = 'block';
                    document.getElementById('completionMessage').scrollIntoView({ behavior: 'smooth', block: 'center' });
                })
                .getPublishedFormUrl(formData.formId);
        }

        function copyFormUrl() {
            const formUrl = document.getElementById('formUrl').textContent;
            navigator.clipboard.writeText(formUrl).then(function() {
                const copyButton = document.querySelector('.copy-button');
                const originalText = copyButton.textContent;
                copyButton.textContent = 'Copied!';
                setTimeout(() => {
                    copyButton.textContent = originalText;
                }, 2000);
            });
        }

        // Function to load documents into dropdown
        function loadDocuments() {
            google.script.run
                .withSuccessHandler(populateDropdown)
                .withFailureHandler(handleLoadError)
                .getAvailableGoogleDocs();
        }

        // Function to populate the dropdown with documents
        function populateDropdown(docs) {
            const selector = document.getElementById('docSelector');
            
            // Clear existing options except the first one
            while (selector.options.length > 1) {
                selector.remove(1);
            }
            
            // Add new options
            docs.forEach(doc => {
                const option = document.createElement('option');
                option.value = doc.id;
                option.text = doc.name;
                selector.add(option);
            });
            
            // Add event listeners for validation
            selector.onchange = validateInputs;
            document.getElementById('aspectInput').onkeyup = validateInputs;
        }

        // Function to validate input fields
        function validateInputs() {
            const docSelector = document.getElementById('docSelector');
            const aspectInput = document.getElementById('aspectInput');
            const generateButton = document.getElementById('generateButton');
            
            const isValid = docSelector.value && aspectInput.value.trim();
            generateButton.disabled = !isValid;
        }

        // Function to handle loading errors
        function handleLoadError(error) {
            showError('Failed to load documents: ' + error);
        }

        // Initialize everything when the page loads
        window.onload = function() {
            loadDocuments();
            document.getElementById('aspectInput').onkeyup = validateInputs;
        };
    </script>
</body>
</html>```

### ./test.gs
```
function logAspectsSheet() {
  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Aspects");
    if (!sheet) {
      Logger.log("❌ Aspects sheet not found!");
      return;
    }
    
    const data = sheet.getDataRange().getValues();
    
    Logger.log("\n📊 Aspects Sheet Contents:");
    Logger.log("------------------------");
    
    // Log headers
    Logger.log("Headers: " + data[0].filter(header => header !== "").join(" | "));
    
    // Log all data with row numbers
    data.forEach((row, index) => {
      if (index === 0) return; // Skip header row
      const rowNum = index + 1;
      const rowData = row.map(cell => cell || "").join(" | ");
      Logger.log(`Row ${rowNum}: ${rowData}`);
    });
    
    // Create a visual representation of the sheet
    Logger.log("\n📋 Sheet Visual Structure:");
    Logger.log("------------------------");
    const visualSheet = data.map(row => 
      row.map(cell => cell || "(empty)").join(" | ")
    ).join("\n");
    Logger.log(visualSheet);
    
    return data;
  } catch (error) {
    Logger.log("❌ Error logging Aspects sheet: " + error);
    return null;
  }
}

function getAspectsFromSheet() {
  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Aspects");
    if (!sheet) {
      Logger.log("❌ Aspects sheet not found!");
      return null;
    }
    
    const data = sheet.getDataRange().getValues();
    if (data.length === 0) {
      Logger.log("❌ Aspects sheet is empty!");
      return null;
    }

    // Get only the headers (first row)
    const headers = data[0].filter(header => header !== "");
    
    Logger.log("\n📊 Aspects Sheet Headers:");
    Logger.log(headers.join(" | "));
    
    if (headers.length === 0) {
      Logger.log("❌ No headers found in Aspects sheet!");
      return null;
    }

    return headers;
  } catch (error) {
    Logger.log("❌ Error in getAspectsFromSheet: " + error);
    return null;
  }
}

function getQuestionsPerAspect(responses) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Aspects");
  if (!sheet) {
    Logger.log("❌ Aspects sheet not found!");
    return null;
  }
  
  const data = sheet.getDataRange().getValues();
  const headers = data[0];
  const aspects = headers.filter(header => header !== "");
  
  // Get the form to access questions in original order
  const form = FormApp.openByUrl(SpreadsheetApp.getActiveSpreadsheet().getFormUrl());
  const formItems = form.getItems();
  
  // Filter and sort questions maintaining form order
  const questions = formItems
    .filter(item => item.getType() !== FormApp.ItemType.SECTION_HEADER)
    .map(item => item.getTitle())
    .filter(q => !["Timestamp", "Mobile", "Name", "Email"].includes(q));
  
  const questionsPerAspect = Math.floor(questions.length / aspects.length);
  
  return {
    aspects,
    questionsPerAspect,
    totalQuestions: questions.length,
    orderedQuestions: questions // Return the ordered questions
  };
}

function generateAssessmentPrompt(categories, responses) {
  if (!categories || categories.length === 0) {
    Logger.log("❌ No categories found for assessment!");
    return null;
  }

  Logger.log("\n📝 Categories for Assessment:");
  categories.forEach(cat => Logger.log("- " + cat));

  // Get questions in original form order
  const form = FormApp.openByUrl(SpreadsheetApp.getActiveSpreadsheet().getFormUrl());
  const formItems = form.getItems();
  const orderedQuestions = formItems
    .filter(item => item.getType() !== FormApp.ItemType.SECTION_HEADER)
    .map(item => item.getTitle())
    .filter(q => !["Timestamp", "Mobile", "Name", "Email"].includes(q));

  // Create ordered responses array maintaining form order
  const orderedResponses = orderedQuestions.map(question => [
    question,
    responses[question] || ''
  ]);

  // Calculate questions per category
  const questionsPerCategory = Math.floor(orderedQuestions.length / categories.length);

  // Create category mapping based on form order
  let categoryMapping = "";
  let startIndex = 0;
  categories.forEach((category, index) => {
    const endIndex = startIndex + questionsPerCategory;
    const categoryQuestions = orderedQuestions.slice(startIndex, endIndex);
    
    categoryMapping += `\n${category}:\n`;
    categoryQuestions.forEach((q, qIndex) => {
      categoryMapping += `${qIndex + 1}. ${q}\n`;
    });
    startIndex = endIndex;
  });

  Logger.log("\n📋 Questions mapped to categories:");
  Logger.log(categoryMapping);

  const promptText = `Please analyze these candidate responses and create an assessment table following these EXACT requirements:

STRICT CATEGORY-QUESTION MAPPING
------------------------------
These questions MUST be assessed under their assigned categories - do not change this mapping:
${categoryMapping}

ASSESSMENT STRUCTURE REQUIREMENTS
------------------------------
1. Each category MUST have exactly ${questionsPerCategory} questions assessed
2. Questions MUST be assessed in the exact order shown above
3. Do not combine or skip any questions
4. Total rows in table must be ${orderedQuestions.length}
5. Questions must remain in their assigned categories - no moving questions between categories

ASSESSMENT FORMAT
---------------
PERFORMANCE ASSESSMENT TABLE
--------------------------
| Question Category | Scenario | This Candidate | Benchmark | Key Performance |
|---|---|---|---|---|

For each question:
1. Question Category: Use exact category name from mapping
2. Scenario: Brief description of question topic (2-4 words)
3. This Candidate: Score in X/10 format
4. Benchmark: Expected score in 0-9 format
5. Key Performance: Brief analysis of response

CANDIDATE RESPONSES
-----------------
${orderedResponses.map(([q, a], index) => `Response ${index + 1}:\nQuestion: ${q}\nAnswer: ${a}`).join('\n\n')}

DETAILED RESPONSES FORMAT
----------------------
After the table, list the detailed responses in the EXACT SAME ORDER as the category-question mapping above:

DETAILED RESPONSES
----------------
[List each question and answer in the exact order shown in the category mapping above]
Question: [Question text]
Answer: [Corresponding answer]`;

  Logger.log("\n✅ Prompt Generation Complete");
  Logger.log("📊 Questions per category:", questionsPerCategory);
  
  return promptText;
}

function getQuestionsPerAspect(responses) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Aspects");
  if (!sheet) {
    Logger.log("❌ Aspects sheet not found!");
    return null;
  }
  
  const data = sheet.getDataRange().getValues();
  const headers = data[0];
  const aspects = headers.filter(header => header !== "");
  
  // Get all questions except personal info
  const questions = Object.keys(responses).filter(q => 
    !["Timestamp", "Mobile", "Name", "Email"].includes(q)
  );
  
  const questionsPerAspect = Math.floor(questions.length / aspects.length);
  
  return {
    aspects,
    questionsPerAspect,
    totalQuestions: questions.length
  };
}

function onFormSubmit(e) {
  var responses = {};
  var namedValues = e.namedValues;
  var spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  var spreadsheetUrl = spreadsheet.getUrl();
  var formTitle = spreadsheet.getName();
  
  var candidateInfo = {
    name: namedValues["Name"] ? namedValues["Name"][0] : "N/A",
    mobile: namedValues["Mobile"] ? namedValues["Mobile"][0] : "N/A",
    email: namedValues["Email"] ? namedValues["Email"][0] : "N/A"
  };
  
  for (var question in namedValues) {
    if (namedValues[question] && namedValues[question].length > 0) {
      responses[question] = namedValues[question][0];
    }
  }

  if (Object.keys(responses).length === 0) {
    Logger.log("No responses found");
    return;
  }

  const categories = getAspectsFromSheet();
  if (!categories) {
    Logger.log("❌ Failed to get categories from sheet. Cannot proceed with assessment.");
    return;
  }

  const promptText = generateAssessmentPrompt(categories, responses);
  if (!promptText) {
    Logger.log("❌ Failed to generate assessment prompt. Cannot proceed.");
    return;
  }

  var apiKey = "AIzaSyB0xf4Fz4rfJkxulI8FdSigeta-y9EdcI4";
  var apiUrl = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent";
  var url = apiUrl + "?key=" + apiKey;

  var headers = {
    "Content-Type": "application/json"
  };

  var requestBody = {
    "contents": [{
      "role": "user",
      "parts": [{"text": promptText}]
    }],
    "generationConfig": {
      "temperature": 0.7,
      "topP": 0.8,
      "topK": 40,
      "maxOutputTokens": 8192,
      "stopSequences": ["DETAILED RESPONSES"] // Add this to prevent extra content
    }
  };

  var options = {
    "method": "POST",
    "headers": headers,
    "payload": JSON.stringify(requestBody),
    "muteHttpExceptions": true
  };

  try {
    var response = UrlFetchApp.fetch(url, options);
    var data = JSON.parse(response.getContentText());

    if (response.getResponseCode() !== 200) {
      Logger.log("Error during API call: " + JSON.stringify(data.error));
      return;
    }

    var output = data.candidates ? data.candidates[0].content.parts[0].text : null;
    if (!output) {
      Logger.log("No content returned by Gemini API");
      return;
    }

    Logger.log("Generated Report: \n" + output);
    saveToSheet(output, responses, candidateInfo);
    sendEmailReport(output, responses, spreadsheetUrl, formTitle, candidateInfo, categories);

  } catch (error) {
    Logger.log("Exception during API call: " + error);
  }
}

function saveToSheet(content, responses, candidateInfo) {
  try {
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Reports");
    if (!sheet) {
      sheet = SpreadsheetApp.getActiveSpreadsheet().insertSheet("Reports");
      sheet.appendRow(["Timestamp", "Name", "Mobile", "Email", "Assessment Report", "Raw Responses"]);
    }
    var timestamp = new Date();
    sheet.appendRow([
      timestamp, 
      candidateInfo.name,
      candidateInfo.mobile,
      candidateInfo.email,
      content, 
      JSON.stringify(responses)
    ]);
  } catch (error) {
    Logger.log("Error saving to sheet: " + error);
  }
}

function sendEmailReport(content, responses, spreadsheetUrl, formTitle, candidateInfo, categories) {
  try {
    const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
    const owner = spreadsheet.getOwner().getEmail();
    
    const defaultRecipients = [
      owner,
      "alfred.lau@gemini.demo.hkmci.com"
    ].filter(Boolean).join(",");
    
    Logger.log(`Sending email to: ${defaultRecipients}`);

    var subject = `Candidate Assessment Report - ${formTitle} - ${candidateInfo.name}`;

    // Get form questions in original order
    const form = FormApp.openByUrl(spreadsheet.getFormUrl());
    const formItems = form.getItems();
    const formQuestions = formItems
      .filter(item => item.getType() !== FormApp.ItemType.SECTION_HEADER)
      .map(item => item.getTitle())
      .filter(title => !["Name", "Mobile", "Email"].includes(title));

    // Extract assessment table content
    const tableContent = content.match(/PERFORMANCE ASSESSMENT TABLE[\s\S]*?(?=\n\nDETAILED RESPONSES|$)/);
    let tableRows = [];
    
    if (tableContent) {
      tableRows = tableContent[0].split('\n')
        .filter(row => row.includes('|'))
        .slice(2); // Skip header and divider rows
    }

    // Create a map of scenarios and their categories from the table
    const scenarioMap = new Map();
    tableRows.forEach(row => {
      const cells = row.split('|');
      if (cells.length >= 3) {
        const category = cells[1].trim();
        const scenario = cells[2].trim();
        scenarioMap.set(scenario, category);
      }
    });

    // Match form questions with table scenarios
    const matchedResponses = formQuestions.map(question => {
      // Find the most relevant scenario for this question
      let bestMatch = null;
      let bestMatchScore = 0;

      scenarioMap.forEach((category, scenario) => {
        const questionWords = question.toLowerCase().split(' ');
        const scenarioWords = scenario.toLowerCase().split(' ');
        
        // Count matching significant words
        const matchScore = questionWords.reduce((score, word) => {
          if (word.length > 3 && scenarioWords.includes(word)) {
            score += 1;
          }
          return score;
        }, 0);

        if (matchScore > bestMatchScore) {
          bestMatchScore = matchScore;
          bestMatch = { scenario, category };
        }
      });

      return {
        question,
        category: bestMatch?.category || 'Uncategorized',
        scenario: bestMatch?.scenario || question.slice(0, 30),
        answer: responses[question] || 'No answer provided'
      };
    });

    // Format the detailed responses section using the original question order
    const formattedResponses = matchedResponses
      .map(({ question, answer }) => 
        `Question: ${question}\nAnswer: ${answer}`
      )
      .join('\n\n');
    
    var body = `
==============================================
CANDIDATE ASSESSMENT REPORT
==============================================

CANDIDATE INFORMATION
-------------------
Name:   ${candidateInfo.name}
Mobile: ${candidateInfo.mobile}
Email:  ${candidateInfo.email}

EVALUATION CATEGORIES
-------------------
${categories.join('\n')}

ASSESSMENT
---------
${content}

DETAILED RESPONSES
----------------
${formattedResponses}

-------------------
Results Sheet: ${spreadsheetUrl}
==============================================`;

    // Convert the markdown table to HTML for email
    var htmlBody = body.replace(/\n/g, '<br>');
    htmlBody = htmlBody.replace(
      /PERFORMANCE ASSESSMENT TABLE\s*-+\s*\|([\s\S]*?)(?=\n\n)/g,
      (match, table) => {
        const rows = table.split('\n').filter(row => row.trim());
        const htmlRows = rows.map(row => {
          const cells = row.split('|').filter(cell => cell.trim());
          return `<tr>${cells.map(cell => 
            `<td style="padding: 8px; border: 1px solid #ddd;">${cell.trim()}</td>`
          ).join('')}</tr>`;
        });
        return `
          <h3>PERFORMANCE ASSESSMENT TABLE</h3>
          <table style="border-collapse: collapse; width: 100%; margin: 20px 0;">
            ${htmlRows.join('\n')}
          </table>
        `;
      }
    );

    // Add email options
    var emailOptions = {
      htmlBody: htmlBody,
      name: "HR Assessment System"
    };

    // Send email using defaultRecipients
    GmailApp.sendEmail(defaultRecipients, subject, body, emailOptions);
    
    Logger.log(`Successfully sent email to: ${defaultRecipients}`);
    
  } catch (error) {
    Logger.log(`Error in sendEmailReport: ${error}`);
    throw error;
  }
}

function testOnFormSubmit() {
  var fakeEvent = {
    namedValues: {
      "Name": ["John Doe"],
      "Mobile": ["12345678"],
      "Email": ["john@example.com"],
      "Question 1": ["Sample response 1"],
      "Question 2": ["Sample response 2"]
    }
  };
  onFormSubmit(fakeEvent);
}```

### ./findEntryIds.gs
```
function findEntryIds(formId) {
  const formUrl = `https://docs.google.com/forms/d/${formId}/viewform`;
  const maxRetries = 3;
  const delay = 500; // milliseconds

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      // Fetch the form HTML content with error handling
      const response = UrlFetchApp.fetch(formUrl, { muteHttpExceptions: true });
      const responseCode = response.getResponseCode();

      if (responseCode === 200) {
        const htmlContent = response.getContentText();

        // Extract form data
        const fbDataMatch = htmlContent.match(/FB_PUBLIC_LOAD_DATA_ = (.*?);\s*<\/script>/);
        if (!fbDataMatch) {
          throw new Error('Form data not found in page');
        }

        // Parse the form data and extract questions
        const formData = JSON.parse(fbDataMatch[1]);
        const questions = formData[1][1];

        // Extract entry IDs
        const entryIds = questions.map(question => {
          if (question[4] && question[4][0]) {
            return 'entry.' + question[4][0][0];
          }
          return null;
        }).filter(id => id !== null);

        Logger.log("Found Entry IDs:");
        Logger.log(entryIds);

        return entryIds;
      } else {
        Logger.log(`Attempt ${attempt}: Received HTTP ${responseCode}`);
        if (attempt === maxRetries) {
          throw new Error(`Failed to fetch form after ${maxRetries} attempts. HTTP ${responseCode}`);
        }
      }
    } catch (error) {
      Logger.log(`Attempt ${attempt}: Error in findEntryIds: ${error.message}`);
      if (attempt === maxRetries) {
        throw error;
      }
    }
    // Wait before retrying
    Utilities.sleep(delay);
  }
}
```

### ./LICENSE
```
MIT License

Copyright (c) 2023 test

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### ./findQuestions.gs
```
// Validate interview questions using Gemini API
function validateInterviewQuestions(questions, aspects) {
  try {
    // Get API key from project properties
    const apiKey = PropertiesService.getScriptProperties().getProperty('GEMINI_API_KEY');
    if (!apiKey) {
      throw new Error('Gemini API key not found in script properties');
    }

    // Check for required fields first
    const requiredFields = ['Name', 'Mobile', 'Email'];
    const hasRequiredFields = requiredFields.every(field => 
      questions.some(q => q.toLowerCase().includes(field.toLowerCase()))
    );

    if (!hasRequiredFields) {
      return {
        isValid: false,
        message: 'Missing required fields (Name, Mobile, Email)'
      };
    }

    // Skip Gemini validation for the basic info fields
    const interviewQuestions = questions.filter(q => 
      !requiredFields.some(field => q.toLowerCase().includes(field.toLowerCase()))
    );

    // Prepare aspects string
    const aspectsList = aspects.split(',').map(a => a.trim()).join(', ');

    // Prepare prompt for Gemini with explicit instructions about response format
    const prompt = `As a recruitment expert, evaluate if ALL these interview questions are suitable for assessing: ${aspectsList}.

You must respond with ONLY a JSON object in this EXACT format (no markdown, no code blocks):
{"isValid": true/false}

Where true means ALL questions are suitable for assessing the given aspects, and false means at least one question is not suitable.

Interview questions to evaluate:
${interviewQuestions.map((q, i) => `${i + 1}. ${q}`).join('\n')}`;

    // Call Gemini API
    const response = callGeminiAPI(prompt, apiKey);
    
    try {
      // Parse the cleaned response
      Logger.log('Attempting to parse response:', response);
      const result = JSON.parse(`{${response}}`);
      
      return {
        isValid: result.isValid,
        message: result.isValid ? 
          'Questions validated successfully' : 
          'Questions do not adequately assess the specified aspects'
      };
    } catch (parseError) {
      Logger.log('JSON parsing error:', parseError);
      throw new Error('Invalid response format from validation service');
    }

  } catch (error) {
    Logger.log(`Error in validateInterviewQuestions: ${error.message}`);
    return {
      isValid: false,
      message: `Validation error: ${error.message}`
    };
  }
}

// Modified findQuestions function to include aspect-based validation
function findQuestions() {
  try {
    const config = getConfig();
    const questionsDoc = DocumentApp.openById(config.QUESTIONS_DOC_ID);
    const questions = questionsDoc.getBody().getText().split('\n')
                     .filter(q => q.trim())
                     .map(q => q.trim());
    
    if (questions.length === 0) {
      throw new Error('No questions found in document');
    }

    // Get aspects from script properties (set during form creation)
    const aspects = PropertiesService.getScriptProperties().getProperty('CURRENT_ASPECTS');
    if (!aspects) {
      throw new Error('Assessment aspects not found');
    }

    // Validate questions with aspects
    const validationResult = validateInterviewQuestions(questions, aspects);
    
    if (!validationResult.isValid) {
      Logger.log('Questions validation failed:', validationResult);
      throw new Error(`Question validation failed: ${validationResult.message}`);
    }

    Logger.log(`Successfully processed ${questions.length} questions`);
    return questions;
  } catch (error) {
    Logger.log(`Error finding questions: ${error.message}`);
    throw error;
  }
}```

### ./finddoc.gs
```
// === findGoogleDocs.gs ===
const CONFIG = getConfig();
function findGoogleDocs() {
  const docs = [];
  
  function processFolder(folder) {
    Logger.log(`Scanning folder: ${folder.getName()}`);
    
    // Get all files in the current folder
    const files = folder.getFiles();
    while (files.hasNext()) {
      const file = files.next();
      // Check if the file is a Google Doc
      if (file.getMimeType() === MimeType.GOOGLE_DOCS) {
        docs.push({
          id: file.getId(),
          name: file.getName(),
          url: file.getUrl(),
          lastUpdated: file.getLastUpdated(),
          folder: folder.getName()
        });
      }
    }
    
    // Recursively process subfolders
    const subFolders = folder.getFolders();
    while (subFolders.hasNext()) {
      processFolder(subFolders.next());
    }
  }
  
  try {
    // Validate PROJECT_FOLDER_ID exists in CONFIG
    if (!CONFIG.PROJECT_FOLDER_ID) {
      throw new Error('PROJECT_FOLDER_ID is not defined in CONFIG');
    }
    
    const rootFolder = DriveApp.getFolderById(CONFIG.PROJECT_FOLDER_ID);
    Logger.log('=========================================');
    Logger.log(`Starting scan in target folder: ${rootFolder.getName()}`);
    Logger.log(`Folder ID: ${CONFIG.PROJECT_FOLDER_ID}`);
    Logger.log('=========================================');
    
    processFolder(rootFolder);
    
    // Sort docs by last updated date (most recent first)
    docs.sort((a, b) => b.lastUpdated - a.lastUpdated);
    
    // Log the results
    Logger.log('=========================================');
    Logger.log('DOCUMENT LIST:');
    Logger.log('=========================================');
    if (docs.length === 0) {
      Logger.log('No Google Docs found in the target folder.');
    } else {
      docs.forEach((doc, index) => {
        Logger.log(`${index + 1}. Document Name: ${doc.name}`);
        Logger.log(`   Location: ${doc.folder}`);
        Logger.log(`   Last Updated: ${doc.lastUpdated.toLocaleString()}`);
        Logger.log(`   ID: ${doc.id}`);
        Logger.log('----------------------------------------');
      });
      Logger.log(`Total documents found: ${docs.length}`);
    }
    
    return docs;
    
  } catch (error) {
    Logger.log(`Error in findGoogleDocs: ${error.message}`);
    throw error;
  }
}

// Test function to display document list
function testListDocs() {
  try {
    Logger.log('Starting document scan...');
    const docs = findGoogleDocs();
    
    Logger.log('=========================================');
    Logger.log('SIMPLE NAME LIST:');
    Logger.log('=========================================');
    if (docs.length === 0) {
      Logger.log('No documents found.');
    } else {
      docs.forEach((doc, index) => {
        Logger.log(`${index + 1}. ${doc.name}`);
      });
    }
    
  } catch (error) {
    Logger.log(`Error in testListDocs: ${error.toString()}`);
  }
}

// Frontend access function
function getAvailableGoogleDocs() {
  try {
    const docs = findGoogleDocs();
    return docs.map(doc => ({
      id: doc.id,
      name: doc.name,
      url: doc.url
    }));
  } catch (error) {
    Logger.log(`Error in getAvailableGoogleDocs: ${error.message}`);
    throw error;
  }
}```

### ./createSheel.gs
```
// === createSheet.gs ===
function createSheetInFolder() {
  try {
    // Get configuration from project settings
    const config = getConfig();
    
    // Get target folder
    const targetFolder = DriveApp.getFolderById(config.TARGET_FOLDER_ID);
    
    // Get the source document name
    const sourceDoc = DocumentApp.openById(config.QUESTIONS_DOC_ID);
    const sourceName = sourceDoc.getName();
    const timestamp = getTimestampSuffix();
    const sheetTitle = `${sourceName} - Responses (${timestamp})`;
    
    // Create copy of template in target folder directly
    const templateFile = DriveApp.getFileById(config.TEMPLATE_SHEET_ID);
    const clonedFile = templateFile.makeCopy(sheetTitle, targetFolder);
    const clonedSheetId = clonedFile.getId();
    
    // Open the cloned spreadsheet
    const spreadsheet = SpreadsheetApp.openById(clonedSheetId);
    
    // Check if Form Questions sheet exists, if not create it
    let sheet = spreadsheet.getSheetByName(config.QUESTIONS_SHEET_NAME);
    if (!sheet) {
      sheet = spreadsheet.insertSheet(config.QUESTIONS_SHEET_NAME);
      Logger.log(`Created new sheet: ${config.QUESTIONS_SHEET_NAME}`);
    }

    // Clear any existing content
    sheet.clear();
    
    // Write questions to the sheet using stored questionsData
    if (questionsData && questionsData.length > 0) {
      sheet.getRange(1, 1, 1, questionsData.length).setValues([questionsData]);
      Logger.log(`Added ${questionsData.length} questions to the sheet`);
    }

    return clonedSheetId;
  } catch (error) {
    Logger.log(`Error in createSheetInFolder: ${error.message}`);
    throw error;
  }
}

function createAspectSheet(sheetId, aspectsStr) {
  try {
    const spreadsheet = SpreadsheetApp.openById(sheetId);
    let aspectSheet;
    
    // Try to get existing Aspects sheet or create new one
    try {
      aspectSheet = spreadsheet.getSheetByName('Aspects');
      if (aspectSheet) {
        aspectSheet.clear();
      } else {
        aspectSheet = spreadsheet.insertSheet('Aspects');
      }
    } catch (e) {
      aspectSheet = spreadsheet.insertSheet('Aspects');
    }
    
    // Process aspects string into array
    const aspects = aspectsStr.split(',')
      .map(aspect => aspect.trim())
      .filter(aspect => aspect.length > 0);
    
    if (aspects.length === 0) {
      throw new Error('No valid aspects provided');
    }
    
    // Set headers
    aspectSheet.getRange(1, 1, 1, aspects.length).setValues([aspects]);
    
    Logger.log(`Created aspect sheet with ${aspects.length} aspects: ${aspects.join(', ')}`);
    return aspectSheet.getSheetId();
    
  } catch (error) {
    Logger.log(`Error in createAspectSheet: ${error.message}`);
    throw error;
  }
}```

### ./config.gs
```
// === config.gs ===

// Configuration keys
const CONFIG_KEYS = {
  TEMPLATE_SHEET_ID: 'TEMPLATE_SHEET_ID',
  QUESTIONS_DOC_ID: 'QUESTIONS_DOC_ID',
  TARGET_FOLDER_ID: 'TARGET_FOLDER_ID',
  QUESTIONS_SHEET_NAME: 'QUESTIONS_SHEET_NAME',
  FORM_TITLE: 'FORM_TITLE',
  GEMINI_API_KEY: 'GEMINI_API_KEY',
  PROJECT_FOLDER_ID: 'PROJECT_FOLDER_ID'  // Added new config key
};

// Get all configuration values
function getConfig() {
  const scriptProperties = PropertiesService.getScriptProperties();
  const properties = scriptProperties.getProperties();
  
  return {
    TEMPLATE_SHEET_ID: properties[CONFIG_KEYS.TEMPLATE_SHEET_ID],
    QUESTIONS_DOC_ID: properties[CONFIG_KEYS.QUESTIONS_DOC_ID],
    TARGET_FOLDER_ID: properties[CONFIG_KEYS.TARGET_FOLDER_ID],
    QUESTIONS_SHEET_NAME: properties[CONFIG_KEYS.QUESTIONS_SHEET_NAME] || 'Form Questions',
    FORM_TITLE: properties[CONFIG_KEYS.FORM_TITLE] || 'Interview Questions Form',
    GEMINI_API_KEY: properties[CONFIG_KEYS.GEMINI_API_KEY],
    PROJECT_FOLDER_ID: properties[CONFIG_KEYS.PROJECT_FOLDER_ID]  // Added new property
  };
}

// Set configuration values
function setConfig(config) {
  const scriptProperties = PropertiesService.getScriptProperties();
  
  // Set each property if provided
  if (config.TEMPLATE_SHEET_ID) scriptProperties.setProperty(CONFIG_KEYS.TEMPLATE_SHEET_ID, config.TEMPLATE_SHEET_ID);
  if (config.QUESTIONS_DOC_ID) scriptProperties.setProperty(CONFIG_KEYS.QUESTIONS_DOC_ID, config.QUESTIONS_DOC_ID);
  if (config.TARGET_FOLDER_ID) scriptProperties.setProperty(CONFIG_KEYS.TARGET_FOLDER_ID, config.TARGET_FOLDER_ID);
  if (config.QUESTIONS_SHEET_NAME) scriptProperties.setProperty(CONFIG_KEYS.QUESTIONS_SHEET_NAME, config.QUESTIONS_SHEET_NAME);
  if (config.FORM_TITLE) scriptProperties.setProperty(CONFIG_KEYS.FORM_TITLE, config.FORM_TITLE);
  if (config.GEMINI_API_KEY) scriptProperties.setProperty(CONFIG_KEYS.GEMINI_API_KEY, config.GEMINI_API_KEY);
  if (config.PROJECT_FOLDER_ID) scriptProperties.setProperty(CONFIG_KEYS.PROJECT_FOLDER_ID, config.PROJECT_FOLDER_ID);  // Added new setter
}

// Initialize default configuration
function initializeConfig() {
  const defaultConfig = {
    QUESTIONS_SHEET_NAME: 'Form Questions',
    FORM_TITLE: 'Interview Questions Form'
  };
  
  const scriptProperties = PropertiesService.getScriptProperties();
  const existingProperties = scriptProperties.getProperties();
  
  // Only set defaults for properties that don't exist
  Object.entries(defaultConfig).forEach(([key, value]) => {
    if (!existingProperties[CONFIG_KEYS[key]]) {
      scriptProperties.setProperty(CONFIG_KEYS[key], value);
    }
  });
}

// Reset all configuration values
function resetConfig() {
  const scriptProperties = PropertiesService.getScriptProperties();
  scriptProperties.deleteAllProperties();
  initializeConfig();
}

// Utility function for timestamp
function getTimestampSuffix() {
  const now = new Date();
  return Utilities.formatDate(now, 'GMT+8', 'yyyyMMdd_HHmmss');
}

// Validate configuration
function validateConfig() {
  const config = getConfig();
  const requiredKeys = ['TEMPLATE_SHEET_ID', 'QUESTIONS_DOC_ID', 'TARGET_FOLDER_ID', 'GEMINI_API_KEY', 'PROJECT_FOLDER_ID'];  // Added to required keys
  const missingKeys = [];
  
  requiredKeys.forEach(key => {
    if (!config[key]) {
      missingKeys.push(key);
    }
  });
  
  if (missingKeys.length > 0) {
    throw new Error(`Missing required configuration values: ${missingKeys.join(', ')}`);
  }
  
  return true;
}```

### ./Code.gs
```
function main(params) {
  try {
    // Validate configuration
    validateConfig();

    // Store aspects for validation
    if (params && params.aspects) {
      PropertiesService.getScriptProperties().setProperty('CURRENT_ASPECTS', params.aspects);
    } else {
      throw new Error('Assessment aspects not provided');
    }
    
    // Step 1: Get and validate questions
    try {
      questionsData = findQuestions();
      if (!questionsData) {
        // 如果没有问题数据，直接返回错误
        return {
          error: '无法获取问题数据',
          status: 'error'
        };
      }
    } catch (error) {
      // 捕获验证失败的错误并返回
      return {
        error: error.message,
        status: 'error'
      };
    }

    // 只有在验证通过后才继续执行后续步骤
    // Step 2: Create sheet and form
    const sheetId = createSheetInFolder();
    Logger.log(`Created sheet ID: ${sheetId}`);

    const formId = createFormInFolder(sheetId);
    Logger.log(`Created form ID: ${formId}`);

    makeFormPublic(formId);

    // Step 3: Get answers
    answersData = suggestAnswers(questionsData);
    Logger.log('\nQuestions and Answers:');
    answersData.questions.forEach((question, index) => {
      Logger.log(`\nQ${index + 1}: ${question}`);
      Logger.log(`A${index + 1}: ${answersData.answers[index]}`);
    });

    // Step 4: Create aspect sheet with provided aspects
    if (params && params.aspects) {
      createAspectSheet(sheetId, params.aspects);
    }

    // Step 5: Get form entry IDs and form URL
    const form = FormApp.openById(formId);
    const formUrl = form.getPublishedUrl();
    const entryIds = findEntryIds(formId);
    Logger.log('Found Entry IDs:');
    Logger.log(entryIds);

    // Step 6: Generate prefilled form link
    const prefilledUrl = generatePrefilledLink(formUrl, entryIds, answersData.answers);
    Logger.log('Generated prefilled form URL:');
    Logger.log(prefilledUrl);

    return {
      sheetId: sheetId,
      formId: formId,
      prefilledUrl: prefilledUrl,
      status: 'success'
    };

  } catch (error) {
    Logger.log(`Error in main function: ${error.message}`);
    return {
      error: error.message,
      status: 'error'
    };
  }
}```


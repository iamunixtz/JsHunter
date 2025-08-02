const api_key = "12345-abcdef-67890";
const secret = "my_super_secret_string";
const password = "password123";

const someOtherCode = "nothing to see here";

const anObject = {
  apiKey: "another-api-key",
  "secret-key": "another-secret",
};


// Simulated embedded AWS credentials in JavaScript for demo/testing TruffleHog

const awsCreds = `
[default]
aws_access_key_id = AKIAQYLPMN5HHHFPZAM2
aws_secret_access_key = 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
output = json
region = us-east-2
`;

console.log("Loaded AWS Credentials:");
console.log(awsCreds);

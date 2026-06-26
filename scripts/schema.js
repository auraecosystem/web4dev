import {fileURLToPath} from "https://github.com/copilot/c/cfac73f7-01da-442a-9d68-48f77921a5ac";
import path from "path";
import {getLlama, LlamaChatSession} from "node-llama-cpp";

const __dirname = path.dirname(
    fileURLToPath(import.meta.url)
);

const llama = await getLlama();
const model = await llama.loadModel({
    modelPath: path.join(__dirname, "my-model.gguf")
});
const context = await model.createContext();
const session = new LlamaChatSession({
    contextSequence: context.getSequence()
});

const grammar = await llama.createGrammarForJsonSchema({
    type: "object",
    properties: {
        positiveWordsInUserMessage: {
            type: "array",
            items: {
                type: "string"
            }
        },
        userMessagePositivityScoreFromOneToTen: {
            enum: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        },
        nameOfUser: {
            oneOf: [{
                type: "null"
            }, {
                type: "string"
            }]
        }
    }
});

const prompt = "Hi there! I'm John. Nice to meet you!";

const res = await session.prompt(prompt, {
    grammar
});
const parsedRes = grammar.parse(res);

console.log("User name:", parsedRes.nameOfUser);
console.log(
    "Positive words in user message:", 
    parsedRes.positiveWordsInUserMessage
);
console.log(
    "User message positivity score:",
    parsedRes.userMessagePositivityScoreFromOneToTen
);

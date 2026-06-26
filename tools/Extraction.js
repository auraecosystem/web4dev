import { z } from "zod";

(async () => {

  // Define your data schema
  const extractionSchema = z.object({
    title: z.string(),
    description: z.string(),
    price: z.string().optional(),
  });
  
  // Extract structured data from product page
  const structuredResult = await anchorClient.agent.task(
    "Extract the product title, description, and price from this Amazon product page",
    {
      taskOptions: {
        outputSchema: z.toJSONSchema(extractionSchema),
        url: "https://www.amazon.com/dp/B0D7D9N7X3",
      },
    }
  );
  
  // Validate the result
  const validatedData = extractionSchema.safeParse(structuredResult);
  if (validatedData.success) {
    console.log("Product title:", validatedData.data.title);
    console.log("Description:", validatedData.data.description);
    console.log("Price:", validatedData.data.price);
  } else {
    console.error("Validation failed:", validatedData.error);
  }
})();

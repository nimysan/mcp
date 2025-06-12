export const runtime = "edge";

export async function GET() {
  return new Response("helloworld", {
    headers: {
      "Content-Type": "text/plain",
    },
  });
}

export type PromptRequest = { prompt: string }
export type PromptResponse = { response: string }

export async function sendPrompt(prompt: string): Promise<string> {
    const response = await fetch('/api/book-recommendation', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt } as PromptRequest),
    })

    if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`)
    }

    const data = (await response.json()) as PromptResponse
    return data.response
}

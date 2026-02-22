export const n8nService = {
    webhookUrl: import.meta.env.VITE_WEBHOOK_URL || '/api/webhook/ingest-audio',
    async uploadRecording(
        blob: Blob,
        title: string,
        protagonist: string,
        language: string,
        priority: string,
        source: string = 'web-pwa'
    ): Promise<boolean> {
        try {
            const params = new URLSearchParams({
                title,
                protagonist,
                language,
                priority,
                source,
                timestamp: new Date().toISOString()
            });
            const url = `${this.webhookUrl}?${params.toString()}`;
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'audio/webm' },
                body: blob,
            });
            if (!response.ok) {
                throw new Error(`Upload failed: ${response.statusText}`);
            }
            return true;
        } catch (error) {
            console.error('n8n Upload Error:', error);
            throw error;
        }
    }
};

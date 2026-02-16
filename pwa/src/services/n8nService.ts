export const n8nService = {
    // Production URL
    webhookUrl: 'https://n8n.amayu.cloud/webhook/ingest-audio',

    async uploadRecording(
        blob: Blob,
        title: string,
        protagonist: string,
        language: string,
        priority: string,
        source: string = 'web-pwa'
    ): Promise<boolean> {
        try {
            const formData = new FormData();
            // 'data' field matches what n8n expects for binary
            formData.append('data', blob, `recording-${Date.now()}.webm`);

            formData.append('title', title);
            formData.append('protagonist', protagonist);
            formData.append('language', language);
            formData.append('priority', priority);
            formData.append('source', source);
            formData.append('timestamp', new Date().toISOString());

            const response = await fetch(this.webhookUrl, {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error(`Upload failed: ${response.statusText}`);
            }

            return true;
        } catch (error) {
            console.error('n8n Upload Error:', error);
            throw error; // Let caller handle fallback to queue
        }
    }
};

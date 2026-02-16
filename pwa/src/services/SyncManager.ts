import { storage } from './storage';
import { n8nService } from './n8nService';

class SyncManager {
    private isSyncing: boolean = false;
    private onlineListener: () => void;

    constructor() {
        this.onlineListener = () => {
            console.log('Network restored. Attempting sync...');
            this.sync();
        };

        window.addEventListener('online', this.onlineListener);

        // Initial check and regular interval check (every 60s) just in case
        this.sync();
        setInterval(() => this.sync(), 60000);
    }

    async sync() {
        if (this.isSyncing || !navigator.onLine) return;

        try {
            this.isSyncing = true;
            const unsynced = await storage.getUnsyncedRecordings();

            if (unsynced.length === 0) {
                console.log('No pending recordings to sync.');
                return;
            }

            console.log(`Found ${unsynced.length} pending recordings. Syncing...`);

            for (const record of unsynced) {
                try {
                    // Provide defaults if metadata is missing
                    const meta = record.metadata || {};

                    await n8nService.uploadRecording(
                        record.blob,
                        record.title,
                        meta.protagonist || 'Usuario',
                        meta.language || 'es',
                        meta.priority || 'normal',
                        'web-pwa-offline-queue'
                    );

                    await storage.updateSyncStatus(record.id, true);
                    console.log(`Synced recording: ${record.title} (${record.id})`);
                    // Release local storage after successful sync.
                    await storage.deleteRecording(record.id);
                } catch (error) {
                    console.error(`Failed to sync recording ${record.id}:`, error);
                    // Continue with next item, don't block queue
                }
            }
        } catch (error) {
            console.error('Sync process error:', error);
        } finally {
            this.isSyncing = false;
        }
    }

    cleanup() {
        window.removeEventListener('online', this.onlineListener);
    }
}

new SyncManager();

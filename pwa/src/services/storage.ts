import { openDB } from 'idb';
import type { DBSchema, IDBPDatabase } from 'idb';

interface VoiceNoteDB extends DBSchema {
    recordings: {
        key: string;
        value: {
            id: string;
            blob: Blob;
            title: string;
            createdAt: string;
            synced: boolean;
            metadata?: any;
        };
        indexes: { 'by-date': string };
    };
}

const DB_NAME = 'voicenote-db';
const STORE_NAME = 'recordings';

class StorageService {
    private dbPromise: Promise<IDBPDatabase<VoiceNoteDB>>;

    constructor() {
        this.dbPromise = openDB<VoiceNoteDB>(DB_NAME, 1, {
            upgrade(db) {
                const store = db.createObjectStore(STORE_NAME, {
                    keyPath: 'id',
                });
                store.createIndex('by-date', 'createdAt');
            },
        });
    }

    async saveRecording(id: string, blob: Blob, title: string, metadata: any = {}) {
        const db = await this.dbPromise;
        await db.put(STORE_NAME, {
            id,
            blob,
            title,
            createdAt: new Date().toISOString(),
            synced: false,
            metadata,
        });
    }

    async getRecording(id: string) {
        const db = await this.dbPromise;
        return db.get(STORE_NAME, id);
    }

    async getAllRecordings() {
        const db = await this.dbPromise;
        return db.getAllFromIndex(STORE_NAME, 'by-date');
    }

    async deleteRecording(id: string) {
        const db = await this.dbPromise;
        await db.delete(STORE_NAME, id);
    }

    async clear() {
        const db = await this.dbPromise;
        await db.clear(STORE_NAME);
    }

    async updateSyncStatus(id: string, synced: boolean) {
        const db = await this.dbPromise;
        const record = await db.get(STORE_NAME, id);
        if (record) {
            record.synced = synced;
            await db.put(STORE_NAME, record);
        }
    }

    async getUnsyncedRecordings() {
        const db = await this.dbPromise;
        const all = await db.getAll(STORE_NAME);
        return all.filter(r => !r.synced);
    }
}

export const storage = new StorageService();

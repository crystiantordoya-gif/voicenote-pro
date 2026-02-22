import React, { useState, useEffect, useRef } from 'react';
import { Mic, Square } from 'lucide-react';
import { recorder } from '../services/audio'; // Fix import path
import { n8nService } from '../services/n8nService';
import { storage } from '../services/storage';
import { v4 as uuidv4 } from 'uuid';

export const Recorder: React.FC = () => {
    const [isRecording, setIsRecording] = useState(false);
    const [duration, setDuration] = useState(0);
    const [isProcessing, setIsProcessing] = useState(false);

    // Form State
    const [title, setTitle] = useState('');
    const [protagonist, setProtagonist] = useState('Usuario');
    const [language, setLanguage] = useState('es');
    const [priority, setPriority] = useState('normal');

    const timerRef = useRef<number | null>(null);

    useEffect(() => {
        return () => {
            if (timerRef.current) clearInterval(timerRef.current);
        };
    }, []);

    const startRecording = async () => {
        try {
            if (!title.trim()) {
                alert('Por favor ingrese un título.');
                return;
            }
            await recorder.start();
            setIsRecording(true);
            setDuration(0);
            timerRef.current = window.setInterval(() => {
                setDuration(prev => prev + 1);
            }, 1000);
        } catch (err) {
            console.error(err);
            alert('Error al acceder al micrófono.');
        }
    };

    const stopRecording = async () => {
        if (timerRef.current) clearInterval(timerRef.current);
        setIsRecording(false);
        setIsProcessing(true);

        try {
            const audioBlob = await recorder.stop(); // Returns WebM Blob
            const id = uuidv4();

            // Save locally first (IndexedDB)
            await storage.saveRecording(id, audioBlob, title, {
                protagonist,
                language,
                priority,
                duration
            });

            // Try upload
            if (navigator.onLine) {
                try {
                    await n8nService.uploadRecording(audioBlob, title, protagonist, language, priority);
                    alert('Grabación subida exitosamente!');
                    await storage.deleteRecording(id);
                    // Optionally mark as synced or delete from local if strict space requirements
                } catch (uploadErr) {
                    console.error(uploadErr);
                    alert('Subida fallida. Guardado localmente en Cola Offline.');
                }
            } else {
                alert('Sin conexión. Guardado en Cola Offline.');
            }

            // Reset
            setTitle('');
            setDuration(0);
        } catch (err) {
            console.error(err);
            alert('Error al procesar la grabación.');
        } finally {
            setIsProcessing(false);
        }
    };

    const formatTime = (seconds: number) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    return (
        <div className="recorder-container" style={{ padding: '20px', maxWidth: '600px', margin: '0 auto' }}>
            <div className="form-group" style={{ marginBottom: '15px' }}>
                <label>Título *</label>
                <input
                    type="text"
                    value={title}
                    onChange={e => setTitle(e.target.value)}
                    placeholder="Ej: Reunión de obra"
                    style={{ width: '100%', padding: '10px', fontSize: '16px', backgroundColor: '#333', color: 'white', border: '1px solid #555' }}
                />
            </div>

            <div className="form-row" style={{ display: 'flex', gap: '10px', marginBottom: '15px' }}>
                <div style={{ flex: 1 }}>
                    <label>Protagonista</label>
                    <input
                        type="text"
                        value={protagonist}
                        onChange={e => setProtagonist(e.target.value)}
                        style={{ width: '100%', padding: '8px', backgroundColor: '#333', color: 'white', border: '1px solid #555' }}
                    />
                </div>
                <div style={{ flex: 1 }}>
                    <label>Idioma</label>
                    <select
                        value={language}
                        onChange={e => setLanguage(e.target.value)}
                        style={{ width: '100%', padding: '8px', backgroundColor: '#333', color: 'white', border: '1px solid #555' }}
                    >
                        <option value="es">Español</option>
                        <option value="en">Inglés</option>
                    </select>
                </div>
            </div>

            <div className="form-row" style={{ display: 'flex', gap: '10px', marginBottom: '15px' }}>
                <div style={{ flex: 1 }}>
                    <label>Prioridad</label>
                    <select
                        value={priority}
                        onChange={e => setPriority(e.target.value)}
                        style={{ width: '100%', padding: '8px', backgroundColor: '#333', color: 'white', border: '1px solid #555' }}
                    >
                        <option value="normal">Normal</option>
                        <option value="high">Alta</option>
                    </select>
                </div>
            </div>

            <div className="timer" style={{ fontSize: '48px', textAlign: 'center', margin: '30px 0', fontFamily: 'monospace' }}>
                {formatTime(duration)}
            </div>

            <div className="controls" style={{ display: 'flex', justifyContent: 'center' }}>
                {!isRecording ? (
                    <button
                        onClick={startRecording}
                        disabled={isProcessing}
                        style={{
                            width: '80px', height: '80px', borderRadius: '50%',
                            backgroundColor: '#ef4444', border: 'none', cursor: 'pointer',
                            display: 'flex', alignItems: 'center', justifyContent: 'center'
                        }}
                    >
                        <Mic size={40} color="white" />
                    </button>
                ) : (
                    <button
                        onClick={stopRecording}
                        style={{
                            width: '80px', height: '80px', borderRadius: '50%',
                            backgroundColor: '#333', border: '2px solid #ef4444', cursor: 'pointer',
                            display: 'flex', alignItems: 'center', justifyContent: 'center'
                        }}
                    >
                        <Square size={32} color="#ef4444" fill="#ef4444" />
                    </button>
                )}
            </div>

            {isProcessing && <p style={{ textAlign: 'center', marginTop: '10px' }}>Procesando...</p>}
        </div>
    );
};

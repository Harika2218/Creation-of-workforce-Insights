import React, { useState, useEffect, useRef } from 'react';
import { QrCode, Camera, AlertCircle, CheckCircle2, RefreshCw, X, ShieldAlert } from 'lucide-react';
import { Modal } from '../common/Modal';
import { Button } from '../common/Button';
import { useToast } from '../../context/ToastContext';

interface QRScannerModalProps {
  isOpen: boolean;
  onClose: () => void;
  onScanSuccess: (token: string) => void;
}

export const QRScannerModal: React.FC<QRScannerModalProps> = ({ isOpen, onClose, onScanSuccess }) => {
  const { showToast } = useToast();
  const videoRef = useRef<HTMLVideoElement>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [cameraState, setCameraState] = useState<'idle' | 'requesting' | 'active' | 'denied' | 'unsupported'>('idle');
  const [manualCode, setManualCode] = useState<string>('');
  const [scanning, setScanning] = useState<boolean>(false);

  useEffect(() => {
    if (!isOpen) {
      // Stop media stream on modal close
      if (stream) {
        stream.getTracks().forEach((track) => track.stop());
        setStream(null);
      }
      setCameraState('idle');
      return;
    }

    startCamera();

    return () => {
      if (stream) {
        stream.getTracks().forEach((track) => track.stop());
      }
    };
  }, [isOpen]);

  const startCamera = async () => {
    if (typeof navigator === 'undefined' || !navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      setCameraState('unsupported');
      return;
    }

    try {
      setCameraState('requesting');
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment', width: { ideal: 640 }, height: { ideal: 480 } },
        audio: false,
      });

      setStream(mediaStream);
      setCameraState('active');

      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
        videoRef.current.play().catch(() => {});
      }
    } catch (err: any) {
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        setCameraState('denied');
      } else {
        setCameraState('unsupported');
      }
    }
  };

  const handleSimulateScan = () => {
    setScanning(true);
    setTimeout(() => {
      setScanning(false);
      const dynamicToken = `QR_KIOSK_LOC001_${Date.now()}`;
      onScanSuccess(dynamicToken);
      onClose();
    }, 1200);
  };

  const handleManualSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!manualCode.trim()) {
      showToast('Please enter the kiosk terminal code.', 'warning');
      return;
    }
    onScanSuccess(manualCode.trim());
    setManualCode('');
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <QrCode size={20} className="text-indigo-400" />
          <span>Kiosk QR Attendance Scanner</span>
        </div>
      }
      maxWidth="480px"
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <p style={{ margin: 0, fontSize: '0.82rem', color: 'var(--text-muted)' }}>
          Scan the dynamic QR code displayed on your office kiosk terminal to authenticate physical presence.
        </p>

        {/* Video Viewport / Permission State */}
        <div
          style={{
            position: 'relative',
            width: '100%',
            height: '240px',
            backgroundColor: '#030712',
            borderRadius: 'var(--radius-md)',
            overflow: 'hidden',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            border: '1px solid var(--border-glass)',
          }}
        >
          {cameraState === 'active' ? (
            <>
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                style={{ width: '100%', height: '100%', objectFit: 'cover' }}
              />
              {/* Scan target viewfinder */}
              <div
                style={{
                  position: 'absolute',
                  width: '160px',
                  height: '160px',
                  border: '2px solid #6366F1',
                  borderRadius: '12px',
                  boxShadow: '0 0 0 9999px rgba(0, 0, 0, 0.45)',
                  pointerEvents: 'none',
                }}
              />
              <div
                style={{
                  position: 'absolute',
                  bottom: '10px',
                  background: 'rgba(0,0,0,0.7)',
                  padding: '4px 10px',
                  borderRadius: '999px',
                  fontSize: '0.72rem',
                  color: '#FFFFFF',
                }}
              >
                Align kiosk QR code inside frame
              </div>
            </>
          ) : cameraState === 'requesting' ? (
            <div style={{ textAlign: 'center', padding: '1rem', color: 'var(--text-muted)' }}>
              <RefreshCw size={24} className="animate-spin mx-auto mb-2 text-indigo-400" />
              <p style={{ fontSize: '0.85rem' }}>Requesting camera permission...</p>
            </div>
          ) : cameraState === 'denied' ? (
            <div style={{ textAlign: 'center', padding: '1.5rem', color: '#FCA5A5' }}>
              <ShieldAlert size={32} className="mx-auto mb-2" />
              <p style={{ fontWeight: 600, fontSize: '0.9rem', margin: 0 }}>Camera Permission Denied</p>
              <p style={{ fontSize: '0.75rem', marginTop: '0.3rem', color: 'var(--text-muted)' }}>
                Please enable camera access in your device browser settings or enter the kiosk terminal code below.
              </p>
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '1.5rem', color: 'var(--text-dim)' }}>
              <Camera size={32} className="mx-auto mb-2" />
              <p style={{ fontSize: '0.85rem', margin: 0 }}>Camera not available on this device</p>
              <p style={{ fontSize: '0.75rem', marginTop: '0.3rem' }}>Use the manual code entry option below.</p>
            </div>
          )}
        </div>

        {/* Scan Simulation for Testing Environments */}
        {cameraState === 'active' && (
          <Button
            variant="outline"
            size="sm"
            onClick={handleSimulateScan}
            isLoading={scanning}
            className="w-full text-xs"
          >
            Verify Kiosk Token
          </Button>
        )}

        {/* Fallback: Manual Terminal Code Entry */}
        <div style={{ paddingTop: '0.75rem', borderTop: '1px solid var(--border-glass)' }}>
          <p style={{ margin: '0 0 0.5rem 0', fontSize: '0.78rem', fontWeight: 600, color: '#FFFFFF' }}>
            Fallback: Enter Kiosk Terminal Code
          </p>
          <form onSubmit={handleManualSubmit} style={{ display: 'flex', gap: '0.5rem' }}>
            <input
              type="text"
              placeholder="e.g. KIOSK-BLR-01"
              value={manualCode}
              onChange={(e) => setManualCode(e.target.value)}
              className="form-control"
              style={{ flex: 1, minHeight: '40px', fontSize: '0.85rem' }}
            />
            <Button type="submit" variant="primary" size="sm">
              Submit
            </Button>
          </form>
        </div>
      </div>
    </Modal>
  );
};

export default QRScannerModal;

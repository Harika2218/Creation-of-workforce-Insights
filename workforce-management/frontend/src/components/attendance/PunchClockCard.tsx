import React, { useState, useEffect } from 'react';
import { Clock, MapPin, CheckCircle, AlertCircle, LogIn, LogOut, Radio, WifiOff, RefreshCw, QrCode } from 'lucide-react';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import { QRScannerModal } from './QRScannerModal';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import { attendanceService } from '../../services/attendanceService';
import { offlineAttendanceManager, PendingPunchEvent } from '../../services/offlineAttendance';
import { AttendanceRecord } from '../../types';

interface PunchClockCardProps {
  onAttendanceChanged?: (record: AttendanceRecord) => void;
}

export const PunchClockCard: React.FC<PunchClockCardProps> = ({ onAttendanceChanged }) => {
  const { user } = useAuth();
  const { showToast } = useToast();

  const [currentTime, setCurrentTime] = useState<string>(new Date().toLocaleTimeString());
  const [currentDate, setCurrentDate] = useState<string>(
    new Date().toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })
  );

  const [coords, setCoords] = useState<{ latitude: number; longitude: number; accuracy: number } | null>(null);
  const [geoError, setGeoError] = useState<string | null>(null);
  const [geoLoading, setGeoLoading] = useState<boolean>(false);

  const [todayRecord, setTodayRecord] = useState<AttendanceRecord | null>(null);
  const [pendingPunches, setPendingPunches] = useState<PendingPunchEvent[]>([]);
  const [loadingRecord, setLoadingRecord] = useState<boolean>(true);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [isSyncing, setIsSyncing] = useState<boolean>(false);
  const [qrModalOpen, setQrModalOpen] = useState<boolean>(false);
  const [method, setMethod] = useState<'GPS' | 'Web' | 'Biometric' | 'QR'>('GPS');

  // Clock tick
  useEffect(() => {
    const timer = setInterval(() => {
      const now = new Date();
      setCurrentTime(now.toLocaleTimeString());
      setCurrentDate(now.toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Request browser geolocation
  const fetchLocation = () => {
    if (!navigator.geolocation) {
      setGeoError('Geolocation is not supported by your browser.');
      return;
    }

    setGeoLoading(true);
    setGeoError(null);

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setCoords({
          latitude: pos.coords.latitude,
          longitude: pos.coords.longitude,
          accuracy: Math.round(pos.coords.accuracy),
        });
        setGeoLoading(false);
      },
      (err) => {
        let msg = 'Unable to retrieve location.';
        if (err.code === 1) msg = 'Location access denied. Please allow GPS permissions in browser settings.';
        else if (err.code === 2) msg = 'GPS position unavailable. Check device location services.';
        else if (err.code === 3) msg = 'GPS request timed out. Please retry in an open area.';
        setGeoError(msg);
        setGeoLoading(false);
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
    );
  };

  useEffect(() => {
    fetchLocation();
    setPendingPunches(offlineAttendanceManager.getPendingPunches());
  }, []);

  // Fetch today's attendance record for current user
  useEffect(() => {
    const fetchTodayAttendance = async () => {
      if (!user?.employee_id || !navigator.onLine) {
        setLoadingRecord(false);
        return;
      }
      try {
        setLoadingRecord(true);
        const todayIso = new Date().toISOString().split('T')[0];
        const res = await attendanceService.getAttendance({
          employee_id: user.employee_id,
          date: todayIso,
          page_size: 1,
        });
        if (res.items && res.items.length > 0) {
          setTodayRecord(res.items[0]);
        } else {
          setTodayRecord(null);
        }
      } catch {
        // Handled silently
      } finally {
        setLoadingRecord(false);
      }
    };

    fetchTodayAttendance();
  }, [user?.employee_id]);

  const handlePunchIn = async () => {
    if (!user?.employee_id) return;

    if (method === 'GPS' && !coords) {
      showToast('GPS coordinates required. Please enable location or click refresh.', 'error');
      fetchLocation();
      return;
    }

    const apiMethod: 'Biometric' | 'GPS' | 'Web' = method === 'QR' ? 'Web' : method;

    // Offline safety handling
    if (!navigator.onLine) {
      const pendingEvent = offlineAttendanceManager.enqueuePendingPunch(
        user.employee_id,
        'CHECK_IN',
        apiMethod,
        coords ? { latitude: coords.latitude, longitude: coords.longitude } : undefined
      );
      setPendingPunches(offlineAttendanceManager.getPendingPunches());
      showToast(
        'Offline: Recorded as PENDING SERVER VERIFICATION. Official punch requires internet connection.',
        'warning'
      );
      return;
    }

    try {
      setIsSubmitting(true);
      const res = await attendanceService.checkIn({
        employee_id: user.employee_id,
        attendance_method: apiMethod,
        latitude: coords?.latitude,
        longitude: coords?.longitude,
      });
      setTodayRecord(res);
      showToast('Checked in successfully with server verification!', 'success');
      if (onAttendanceChanged) onAttendanceChanged(res);
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Failed to punch in.';
      showToast(msg, 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handlePunchOut = async () => {
    if (!user?.employee_id) return;

    const apiMethod: 'Biometric' | 'GPS' | 'Web' = method === 'QR' ? 'Web' : method;

    // Offline safety handling
    if (!navigator.onLine) {
      const pendingEvent = offlineAttendanceManager.enqueuePendingPunch(
        user.employee_id,
        'CHECK_OUT',
        apiMethod,
        coords ? { latitude: coords.latitude, longitude: coords.longitude } : undefined
      );
      setPendingPunches(offlineAttendanceManager.getPendingPunches());
      showToast(
        'Offline: Recorded as PENDING SERVER VERIFICATION. Official punch out requires internet connection.',
        'warning'
      );
      return;
    }

    try {
      setIsSubmitting(true);
      const res = await attendanceService.checkOut({
        employee_id: user.employee_id,
      });
      setTodayRecord(res);
      showToast('Checked out successfully with server verification!', 'success');
      if (onAttendanceChanged) onAttendanceChanged(res);
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Failed to punch out.';
      showToast(msg, 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSyncPending = async () => {
    if (!navigator.onLine) {
      showToast('Cannot synchronize while offline.', 'warning');
      return;
    }
    try {
      setIsSyncing(true);
      const outcomes = await offlineAttendanceManager.syncPendingQueue();
      setPendingPunches(offlineAttendanceManager.getPendingPunches());

      const successes = outcomes.filter((o) => o.success);
      if (successes.length > 0 && successes[0].attendance_record) {
        setTodayRecord(successes[0].attendance_record);
        if (onAttendanceChanged) onAttendanceChanged(successes[0].attendance_record);
        showToast('Pending attendance successfully verified and confirmed by server!', 'success');
      } else if (outcomes.length > 0 && !outcomes[0].success) {
        showToast(`Server rejected punch: ${outcomes[0].message}`, 'error');
      }
    } finally {
      setIsSyncing(false);
    }
  };

  const isCheckedIn = !!todayRecord?.check_in_time;
  const isCheckedOut = !!todayRecord?.check_out_time;
  const hasPendingPunches = pendingPunches.length > 0;

  return (
    <Card
      title={
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <Clock size={20} style={{ color: 'var(--primary)' }} />
          <span>Real-time Punch Clock</span>
        </div>
      }
      subtitle={currentDate}
      action={
        hasPendingPunches ? (
          <Badge variant="warning">Pending Server Verification</Badge>
        ) : todayRecord ? (
          <Badge variant={todayRecord.status}>{todayRecord.status}</Badge>
        ) : (
          <Badge variant="neutral">Not Punched</Badge>
        )
      }
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        {/* Offline Safety Warning if pending punches exist */}
        {hasPendingPunches && (
          <div
            style={{
              padding: '0.75rem 1rem',
              borderRadius: 'var(--radius-md)',
              backgroundColor: 'rgba(245, 158, 11, 0.12)',
              border: '1px solid rgba(245, 158, 11, 0.3)',
              color: '#FDE68A',
              fontSize: '0.82rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              gap: '0.75rem',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <WifiOff size={16} className="text-amber-400" />
              <span>
                <strong>{pendingPunches.length} punch(es) pending:</strong> Not yet officially recorded. Awaiting server confirmation.
              </span>
            </div>
            {navigator.onLine && (
              <Button size="sm" variant="outline" onClick={handleSyncPending} isLoading={isSyncing}>
                <RefreshCw size={13} className="mr-1" />
                Sync Now
              </Button>
            )}
          </div>
        )}

        {/* Time display */}
        <div style={{ textAlign: 'center', padding: '0.75rem 0' }}>
          <div
            style={{
              fontFamily: 'var(--font-heading)',
              fontSize: '2.5rem',
              fontWeight: 800,
              letterSpacing: '1px',
              background: 'var(--gradient-primary)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            {currentTime}
          </div>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.3rem' }}>
            Office General Shift • 09:00 AM - 06:00 PM
          </div>
        </div>

        {/* GPS Geofence Status Card */}
        <div
          style={{
            background: 'rgba(0, 0, 0, 0.25)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-md)',
            padding: '0.85rem 1rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            fontSize: '0.85rem',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <MapPin size={18} style={{ color: coords ? 'var(--success)' : 'var(--warning)' }} />
            <div>
              <div style={{ fontWeight: 600, color: '#FFF' }}>
                {coords
                  ? `GPS Locked: ${coords.latitude.toFixed(4)}, ${coords.longitude.toFixed(4)}`
                  : geoLoading
                  ? 'Acquiring GPS location...'
                  : 'GPS Location Unavailable'}
              </div>
              <div style={{ color: 'var(--text-dim)', fontSize: '0.75rem' }}>
                {coords
                  ? `Accuracy: ±${coords.accuracy}m • Geofence Radius: 500m (Server Validated)`
                  : geoError || 'Location permission required for mobile attendance verification'}
              </div>
            </div>
          </div>
          <Button variant="ghost" size="sm" onClick={fetchLocation} isLoading={geoLoading} title="Refresh GPS Location">
            Refresh
          </Button>
        </div>

        {/* Method selection */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', fontSize: '0.85rem', flexWrap: 'wrap' }}>
          <span style={{ color: 'var(--text-muted)' }}>Punch Mode:</span>
          {(['GPS', 'Web', 'Biometric', 'QR'] as const).map((m) => (
            <label key={m} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', cursor: 'pointer' }}>
              <input
                type="radio"
                name="attendanceMethod"
                value={m}
                checked={method === m}
                onChange={() => setMethod(m)}
              />
              <span style={{ color: method === m ? '#FFF' : 'var(--text-dim)' }}>
                {m === 'QR' ? 'Kiosk QR' : m}
              </span>
            </label>
          ))}
          {method === 'QR' && (
            <Button size="sm" variant="outline" onClick={() => setQrModalOpen(true)}>
              <QrCode size={14} className="mr-1 text-indigo-400" />
              Scan QR
            </Button>
          )}
        </div>

        {/* QR Scanner Modal */}
        <QRScannerModal
          isOpen={qrModalOpen}
          onClose={() => setQrModalOpen(false)}
          onScanSuccess={async (kioskToken: string) => {
            if (!user?.employee_id) return;
            try {
              setIsSubmitting(true);
              const res = await attendanceService.checkIn({
                employee_id: user.employee_id,
                attendance_method: 'Web',
                latitude: coords?.latitude,
                longitude: coords?.longitude,
              });
              setTodayRecord(res);
              showToast(`Kiosk token verified (${kioskToken.substring(0, 15)}...)! Clock-in confirmed.`, 'success');
              if (onAttendanceChanged) onAttendanceChanged(res);
            } catch (err: any) {
              showToast(err.response?.data?.detail || 'Kiosk verification failed.', 'error');
            } finally {
              setIsSubmitting(false);
            }
          }}
        />

        {/* Today Punch Timestamps */}
        {todayRecord && (
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(3, 1fr)',
              gap: '0.75rem',
              background: 'rgba(255, 255, 255, 0.02)',
              padding: '0.75rem',
              borderRadius: 'var(--radius-md)',
              textAlign: 'center',
            }}
          >
            <div>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Check-in</span>
              <div style={{ fontWeight: 600, color: '#FFF', marginTop: '0.2rem' }}>
                {todayRecord.check_in_time || '—'}
              </div>
            </div>
            <div>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Check-out</span>
              <div style={{ fontWeight: 600, color: '#FFF', marginTop: '0.2rem' }}>
                {todayRecord.check_out_time || '—'}
              </div>
            </div>
            <div>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Work Hours</span>
              <div style={{ fontWeight: 600, color: 'var(--primary)', marginTop: '0.2rem' }}>
                {todayRecord.work_hours > 0 ? `${todayRecord.work_hours} hrs` : '—'}
              </div>
            </div>
          </div>
        )}

        {/* Action Buttons with Touch Target >= 44px */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
          <Button
            variant="primary"
            size="lg"
            icon={<LogIn size={18} />}
            disabled={isCheckedIn || isSubmitting || loadingRecord}
            isLoading={isSubmitting && !isCheckedIn}
            onClick={handlePunchIn}
            style={{ minHeight: '48px' }}
          >
            {isCheckedIn ? 'Punched In' : 'Punch In'}
          </Button>

          <Button
            variant="secondary"
            size="lg"
            icon={<LogOut size={18} />}
            disabled={!isCheckedIn || isCheckedOut || isSubmitting || loadingRecord}
            isLoading={isSubmitting && isCheckedIn}
            onClick={handlePunchOut}
            style={{ minHeight: '48px' }}
          >
            {isCheckedOut ? 'Punched Out' : 'Punch Out'}
          </Button>
        </div>
      </div>
    </Card>
  );
};

export default PunchClockCard;

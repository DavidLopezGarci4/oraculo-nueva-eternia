import React, { useState } from 'react';
import { renewSSLCertificate, type SSLStatus } from '../../api/admin';

interface SSLWarningModalProps {
  sslStatus: SSLStatus;
  onDismiss: () => void;
  onNavigateToConfig: () => void;
}

export const SSLWarningModal: React.FC<SSLWarningModalProps> = ({
  sslStatus,
  onDismiss,
  onNavigateToConfig,
}) => {
  const [isRenewing, setIsRenewing] = useState(false);
  const [renewalSuccess, setRenewalSuccess] = useState<boolean | null>(null);
  const [feedbackMessage, setFeedbackMessage] = useState<string>('');

  const days = sslStatus.days_remaining ?? 0;
  const isExpired = days <= 0;

  const handleRenew = async () => {
    setIsRenewing(true);
    setFeedbackMessage('');
    try {
      const res = await renewSSLCertificate(true);
      if (res.status === 'success') {
        setRenewalSuccess(true);
        setFeedbackMessage('¡Solicitud de renovación enviada con éxito! Se está procesando en segundo plano.');
      } else {
        setRenewalSuccess(false);
        setFeedbackMessage(res.message || 'Error al iniciar la renovación.');
      }
    } catch (err: any) {
      setRenewalSuccess(false);
      setFeedbackMessage(err.response?.data?.detail || err.message || 'Error de red al contactar con la API.');
    } finally {
      setIsRenewing(false);
    }
  };

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(5, 7, 10, 0.85)',
        backdropFilter: 'blur(8px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 99999,
        padding: '1rem',
      }}
    >
      <div
        style={{
          background: 'linear-gradient(180deg, #1b2332 0%, #121824 100%)',
          borderRadius: '16px',
          border: '1px solid rgba(245, 158, 11, 0.3)',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.7)',
          maxWidth: '520px',
          width: '100%',
          padding: '2rem',
          color: '#f3f4f6',
          fontFamily: 'inherit',
          position: 'relative',
        }}
      >
        {/* Header Icon & Title */}
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem', marginBottom: '1.25rem' }}>
          <div
            style={{
              width: '48px',
              height: '48px',
              borderRadius: '12px',
              backgroundColor: isExpired ? 'rgba(239, 68, 68, 0.15)' : 'rgba(245, 158, 11, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '1.5rem',
              flexShrink: 0,
            }}
          >
            {isExpired ? '🚨' : '🔒'}
          </div>
          <div>
            <h3 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 700, color: '#ffffff' }}>
              {isExpired ? 'Certificado SSL Caducado' : 'Alerta de Seguridad: Certificado SSL'}
            </h3>
            <p style={{ margin: '0.25rem 0 0', fontSize: '0.875rem', color: '#9ca3af' }}>
              Dominio: <code style={{ color: '#fbbf24' }}>{sslStatus.domain || 'oraculo-eternia.duckdns.org'}</code>
            </p>
          </div>
        </div>

        {/* Status / Urgency Box */}
        <div
          style={{
            backgroundColor: 'rgba(15, 23, 42, 0.6)',
            borderRadius: '10px',
            padding: '1rem',
            marginBottom: '1.5rem',
            border: '1px solid rgba(255, 255, 255, 0.06)',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
            <span style={{ fontSize: '0.875rem', color: '#d1d5db' }}>Vigencia restante:</span>
            <span
              style={{
                fontSize: '0.925rem',
                fontWeight: 700,
                color: isExpired ? '#ef4444' : days <= 7 ? '#f97316' : '#f59e0b',
              }}
            >
              {isExpired ? '0 días (Caducado)' : `${days} días (${days <= 7 ? 'Crítico: menos de 1 semana' : 'Menos de 2 semanas'})`}
            </span>
          </div>

          {/* Urgency Progress Bar */}
          <div
            style={{
              width: '100%',
              height: '8px',
              backgroundColor: 'rgba(255, 255, 255, 0.1)',
              borderRadius: '4px',
              overflow: 'hidden',
            }}
          >
            <div
              style={{
                height: '100%',
                width: `${Math.max(5, Math.min(100, (days / 90) * 100))}%`,
                backgroundColor: isExpired ? '#ef4444' : days <= 7 ? '#f97316' : '#f59e0b',
                transition: 'width 0.3s ease',
              }}
            />
          </div>

          <p style={{ margin: '0.75rem 0 0', fontSize: '0.8rem', color: '#9ca3af', lineHeight: 1.4 }}>
            {isExpired
              ? 'El certificado SSL ha caducado. Es necesario renovarlo inmediatamente para mantener el acceso HTTPS seguro.'
              : 'Se recomienda renovar el certificado antes de alcanzar los 7 días para evitar cortes en el servicio HTTPS de Nueva Eternia.'}
          </p>
        </div>

        {/* Feedback Message */}
        {feedbackMessage && (
          <div
            style={{
              padding: '0.75rem 1rem',
              borderRadius: '8px',
              fontSize: '0.875rem',
              marginBottom: '1.25rem',
              backgroundColor: renewalSuccess ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
              color: renewalSuccess ? '#34d399' : '#f87171',
              border: `1px solid ${renewalSuccess ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
            }}
          >
            {feedbackMessage}
          </div>
        )}

        {/* Action Buttons */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          <button
            onClick={handleRenew}
            disabled={isRenewing || renewalSuccess === true}
            style={{
              width: '100%',
              padding: '0.75rem 1.25rem',
              borderRadius: '10px',
              backgroundColor: isRenewing ? '#4b5563' : '#d97706',
              color: '#ffffff',
              fontWeight: 600,
              fontSize: '0.95rem',
              border: 'none',
              cursor: isRenewing || renewalSuccess === true ? 'not-allowed' : 'pointer',
              transition: 'background 0.2s ease',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.5rem',
            }}
          >
            {isRenewing ? (
              <>
                <span style={{ display: 'inline-block', animation: 'spin 1s linear infinite' }}>⏳</span>
                Invocando Renovación SSL...
              </>
            ) : renewalSuccess ? (
              <>✅ Proceso Iniciado</>
            ) : (
              <>⚡ Renovar Certificados Ahora</>
            )}
          </button>

          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button
              onClick={() => {
                onDismiss();
                onNavigateToConfig();
              }}
              style={{
                flex: 1,
                padding: '0.625rem 1rem',
                borderRadius: '8px',
                backgroundColor: 'rgba(255, 255, 255, 0.05)',
                color: '#e5e7eb',
                fontSize: '0.85rem',
                border: '1px solid rgba(255, 255, 255, 0.15)',
                cursor: 'pointer',
              }}
            >
              📊 Ver Diagnóstico
            </button>
            <button
              onClick={onDismiss}
              style={{
                flex: 1,
                padding: '0.625rem 1rem',
                borderRadius: '8px',
                backgroundColor: 'transparent',
                color: '#9ca3af',
                fontSize: '0.85rem',
                border: 'none',
                cursor: 'pointer',
              }}
            >
              Recordar más tarde
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SSLWarningModal;

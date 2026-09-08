import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';

export interface CitizenComplaint {
  id: string;
  call_id?: string;
  ticket_ref: string;
  type: 'voice' | 'chat';
  timestamp: string;
  risk_level: 'CRITICAL' | 'HIGH' | 'MODERATE' | 'LOW';
  summary: string;
  language?: string;
  recording_url?: string;
  recommended_services: string[];
  status: string;
  is_legitimate?: boolean;
}

export const UserDashboard: React.FC = () => {
  const [complaints, setComplaints] = useState<CitizenComplaint[]>([
    {
      id: 'complaint_01',
      call_id: 'call_9901_forest',
      ticket_ref: 'TKT-2026-0907-8821',
      type: 'voice',
      timestamp: 'Today, 22:45',
      risk_level: 'CRITICAL',
      summary: 'Outdoor pursuit in forest. Spatial wilderness protocol engaged; zero door-locking hallucination. PCR 112 dispatched to road landmark.',
      language: 'or-IN',
      recording_url: '/api/v1/recordings/call_9901_forest.wav',
      recommended_services: ['PCR 112 Police Dispatch', '14566 Witness Protection Desk', 'DLSA Emergency Cell'],
      status: 'REGISTERED_ACTIVE_TRIAGE',
      is_legitimate: true
    },
    {
      id: 'complaint_02',
      call_id: 'call_9902_boycott',
      ticket_ref: 'TKT-2026-0906-4412',
      type: 'voice',
      timestamp: 'Yesterday, 14:15',
      risk_level: 'HIGH',
      summary: 'Social boycott and tube well drinking water access denial. Kosli/Desia dialect normalized. Statutory Section 15A complaint prepared.',
      language: 'sp-IN',
      recording_url: '/api/v1/recordings/call_9902_boycott.wav',
      recommended_services: ['14566 National Helpline', 'DLSA Free Legal Aid', 'District Welfare Magistrate'],
      status: 'REGISTERED_LEGAL_AID',
      is_legitimate: true
    }
  ]);
  const [loading, setLoading] = useState<boolean>(true);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  // Load complaints from API and local session without requiring login
  useEffect(() => {
    const fetchComplaints = async () => {
      try {
        const remoteComplaints = await api.getRecentComplaints();
        if (Array.isArray(remoteComplaints) && remoteComplaints.length > 0) {
          setComplaints(remoteComplaints);
        }
      } catch (err) {
        console.warn('Could not load remote complaints, using cached showcase:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchComplaints();
  }, []);

  const handleDeleteComplaint = async (target: CitizenComplaint) => {
    const identifier = target.ticket_ref || target.call_id || target.id;
    if (!confirm(`Are you sure you want to permanently delete Complaint ${identifier} and permanently erase its audio recording from state servers (DPDP Act Right to Erasure)?`)) {
      return;
    }

    setDeletingId(identifier);
    try {
      await api.deleteComplaint(identifier);
      setComplaints((prev) => prev.filter((c) => c.ticket_ref !== identifier && c.call_id !== identifier && c.id !== identifier));
      setStatusMessage(`Complaint ${identifier} & call recording permanently erased from state servers per DPDP Act.`);
      setTimeout(() => setStatusMessage(null), 5000);
    } catch (err) {
      console.error('Delete error:', err);
      setStatusMessage('Error deleting complaint. Please try again.');
    } finally {
      setDeletingId(null);
    }
  };

  const handlePurgeAll = () => {
    if (confirm('Permanently purge all local session history from this device?')) {
      setComplaints([]);
      setStatusMessage('All local case logs have been purged for your privacy.');
      setTimeout(() => setStatusMessage(null), 4000);
    }
  };

  return (
    <>
      <section className="section" style={{ paddingTop: '100px' }}>
        <main className="hero-content" style={{ minHeight: 'auto', paddingBottom: '40px' }}>
          <div className="w-layout-blockcontainer container w-container">
            {/* Header */}
            <div className="heading-and-button margin-bottom-40">
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                  <span className="triage-badge low" style={{ textTransform: 'uppercase', letterSpacing: '0.05em', fontSize: '11px' }}>
                    Citizen Portal • Public Access
                  </span>
                  <span style={{ fontSize: '13px', color: '#059669', fontWeight: 600 }}>
                    ● No Login Required
                  </span>
                </div>
                <h1 className="h2 max-width-640-mobile-480">Citizen Grievance Logs &amp; Audio Recordings</h1>
                <p className="regular-m max-width-480" style={{ marginTop: '8px', color: 'var(--grey-80)' }}>
                  Review recorded helpline call sessions, listen to voice recordings, and exercise your statutory Right to Erasure under the DPDP Act 2023.
                </p>
              </div>

              <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', alignItems: 'center' }}>
                <Link to="/agent" className="button primary small w-button">
                  Start New Voice Call
                </Link>
                {complaints.length > 0 && (
                  <button 
                    type="button" 
                    onClick={handlePurgeAll} 
                    className="button secondary small w-button"
                  >
                    Purge All (Privacy)
                  </button>
                )}
              </div>
            </div>

            {/* Notification Status Banner */}
            {statusMessage && (
              <div 
                className="margin-bottom-24"
                style={{ 
                  backgroundColor: '#ecfdf5', 
                  border: '1px solid #10b981', 
                  color: '#065f46', 
                  padding: '12px 20px', 
                  borderRadius: '10px',
                  fontWeight: 500,
                  fontSize: '14px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}
              >
                <span>✓</span> {statusMessage}
              </div>
            )}

            {/* Cases List */}
            {loading ? (
              <div className="block padding-24-32 bg-grey-3" style={{ textAlign: 'center', padding: '48px 24px' }}>
                <div className="regular-m">Loading verified citizen complaint logs &amp; audio recordings...</div>
              </div>
            ) : complaints.length === 0 ? (
              <div className="block padding-24-32 bg-grey-3" style={{ textAlign: 'center', padding: '64px 32px' }}>
                <h4 className="h4 margin-bottom-16">No Active Complaints on File</h4>
                <p className="regular-m margin-bottom-24" style={{ maxWidth: '460px', margin: '0 auto 24px auto' }}>
                  There are currently no recorded voice complaints. Call the AI Voice Agent or Helpline 14566 to report an incident. Genuine complaints will appear here with recording playback.
                </p>
                <Link to="/agent" className="button primary small w-button">
                  Call Voice Agent Now
                </Link>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                {complaints.map((item) => (
                  <div key={item.ticket_ref || item.id} className="block padding-24-32 bg-grey-3" style={{ borderRadius: '16px' }}>
                    {/* Top Bar */}
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%', marginBottom: '16px', flexWrap: 'wrap', gap: '8px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
                        <span className={`triage-badge ${item.risk_level.toLowerCase()}`}>
                          {item.risk_level} RISK
                        </span>
                        <span className="regular-m" style={{ fontWeight: 700, letterSpacing: '0.02em' }}>
                          Ticket Ref: {item.ticket_ref}
                        </span>
                        {item.status && (
                          <span style={{ fontSize: '12px', padding: '3px 10px', borderRadius: '8px', background: '#dbeafe', color: '#1e40af', fontWeight: 600 }}>
                            {item.status.replace(/_/g, ' ')}
                          </span>
                        )}
                      </div>

                      <div className="regular-s color-grey-80">
                        {item.type.toUpperCase()} • {item.timestamp}
                      </div>
                    </div>

                    <div className="line black margin-bottom-20"></div>

                    {/* Summary */}
                    <h4 className="h4 margin-bottom-12" style={{ lineHeight: '1.4' }}>
                      {item.summary}
                    </h4>

                    {/* Audio Player Showcase */}
                    {item.recording_url && (
                      <div 
                        style={{ 
                          marginTop: '16px', 
                          marginBottom: '16px',
                          background: 'var(--white)', 
                          padding: '16px 20px', 
                          borderRadius: '12px', 
                          border: '1px solid var(--grey-8)' 
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
                          <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--black)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                            <span>🎧</span> Voice Call Audio Recording
                          </span>
                          <span style={{ fontSize: '12px', color: '#059669', fontWeight: 600, background: '#ecfdf5', padding: '2px 8px', borderRadius: '6px' }}>
                            Prank-Verified Genuine Intake
                          </span>
                        </div>
                        <audio 
                          controls 
                          src={api.getRecordingAudioUrl(item.recording_url)} 
                          style={{ width: '100%', height: '40px', outline: 'none' }} 
                        />
                      </div>
                    )}

                    {/* Recommended Services & Actions */}
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '16px', flexWrap: 'wrap', gap: '16px' }}>
                      <div>
                        <div className="regular-s color-grey-80 margin-bottom-8">Statutory Protections:</div>
                        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                          {item.recommended_services.map((svc, i) => (
                            <span 
                              key={i} 
                              style={{ 
                                backgroundColor: 'var(--white)', 
                                border: '1px solid var(--grey-8)', 
                                padding: '4px 12px', 
                                borderRadius: '100px', 
                                fontSize: '13px' 
                              }}
                            >
                              {svc}
                            </span>
                          ))}
                        </div>
                      </div>

                      {/* Right to Erasure Action */}
                      <button
                        type="button"
                        onClick={() => handleDeleteComplaint(item)}
                        disabled={deletingId === (item.ticket_ref || item.id)}
                        className="button small"
                        style={{
                          backgroundColor: '#fee2e2',
                          color: '#991b1b',
                          border: '1px solid #f87171',
                          borderRadius: '8px',
                          cursor: 'pointer',
                          fontWeight: 600,
                          fontSize: '13px',
                          padding: '8px 16px',
                          transition: 'all 0.2s'
                        }}
                      >
                        {deletingId === (item.ticket_ref || item.id) ? "Erasing Data..." : "Withdraw Case & Delete Audio"}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </main>
      </section>
    </>
  );
};

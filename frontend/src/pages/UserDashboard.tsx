import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

interface CaseLog {
  id: string;
  ticket_ref: string;
  type: 'voice' | 'chat';
  timestamp: string;
  risk_level: 'CRITICAL' | 'HIGH' | 'LOW';
  summary: string;
  recommended_services: string[];
}

export const UserDashboard: React.FC = () => {
  const [logs, setLogs] = useState<CaseLog[]>([
    {
      id: 'sess_01',
      ticket_ref: 'TKT-2026-0907-8821',
      type: 'voice',
      timestamp: 'Today, 22:45',
      risk_level: 'CRITICAL',
      summary: 'Outdoor pursuit in forest. Spatial wilderness protocol engaged; zero door-locking hallucination. PCR 112 dispatched to road landmark.',
      recommended_services: ['PCR 112 Police Dispatch', '14566 Witness Protection Desk', 'DLSA Emergency Cell']
    },
    {
      id: 'sess_02',
      ticket_ref: 'TKT-2026-0906-4412',
      type: 'chat',
      timestamp: 'Yesterday, 14:15',
      risk_level: 'HIGH',
      summary: 'Social boycott and tube well drinking water access denial. Kosli dialect normalized. Statutory Section 15A complaint prepared.',
      recommended_services: ['14566 National Helpline', 'DLSA Free Legal Aid', 'District Welfare Magistrate']
    }
  ]);
  const navigate = useNavigate();

  const handlePurge = () => {
    if (confirm('Are you sure you want to permanently purge your local session history?')) {
      setLogs([]);
    }
  };

  const handleSignOut = () => {
    sessionStorage.removeItem('sahay_user');
    navigate('/login');
  };

  return (
    <>
      <section className="section" style={{ paddingTop: '100px' }}>
        <main className="hero-content" style={{ minHeight: 'auto', paddingBottom: '40px' }}>
          <div className="w-layout-blockcontainer container w-container">
            <div className="heading-and-button margin-bottom-56">
              <div>
                <div className="regular-m margin-bottom-12" style={{ textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  Citizen Portal
                </div>
                <h2 className="h2 max-width-432-mobile-320">My Triage Logs &amp; Cases</h2>
              </div>
              <div style={{ display: 'flex', gap: '12px' }}>
                <button 
                  type="button" 
                  onClick={handlePurge} 
                  className="button secondary small w-button"
                >
                  Purge History (Privacy)
                </button>
                <button 
                  type="button" 
                  onClick={handleSignOut} 
                  className="button primary small w-button"
                >
                  Sign Out
                </button>
              </div>
            </div>

            {/* Case Logs Grid */}
            {logs.length === 0 ? (
              <div className="block padding-24-32 bg-grey-3" style={{ textAlign: 'center', padding: '64px 32px' }}>
                <h4 className="h4 margin-bottom-16">No Recorded Sessions</h4>
                <p className="regular-m margin-bottom-24">
                  Your interaction logs are completely empty or have been purged for your privacy.
                </p>
                <Link to="/agent" className="button primary small w-button">
                  Start New Triage Session
                </Link>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                {logs.map((log) => (
                  <div key={log.id} className="block padding-24-32 bg-grey-3">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%', marginBottom: '16px' }}>
                      <div>
                        <span className={`triage-badge ${log.risk_level.toLowerCase()}`}>
                          {log.risk_level} RISK
                        </span>
                        <span className="regular-m" style={{ marginLeft: '12px', fontWeight: 600 }}>
                          Ticket: {log.ticket_ref}
                        </span>
                      </div>
                      <div className="regular-s color-grey-80">
                        {log.type.toUpperCase()} • {log.timestamp}
                      </div>
                    </div>

                    <div className="line black margin-bottom-20"></div>

                    <h4 className="h4 margin-bottom-12">{log.summary}</h4>

                    <div style={{ marginTop: '16px', width: '100%' }}>
                      <div className="regular-s color-grey-80 margin-bottom-12">Recommended Statutory Services:</div>
                      <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                        {log.recommended_services.map((svc, i) => (
                          <span 
                            key={i} 
                            style={{ 
                              backgroundColor: 'var(--white)', 
                              border: '1px solid var(--grey-8)', 
                              padding: '6px 14px', 
                              borderRadius: '100px', 
                              fontSize: '14px' 
                            }}
                          >
                            {svc}
                          </span>
                        ))}
                      </div>
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

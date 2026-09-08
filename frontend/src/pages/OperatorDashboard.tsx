import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

interface QueueItem {
  id: string;
  call_id: string;
  caller_number: string;
  channel: string;
  timestamp: string;
  risk_level: 'CRITICAL' | 'HIGH' | 'LOW';
  svi_score: number;
  emotion: { fear: number; sadness: number; anger: number; neutral: number };
  acoustic: { pitch_f0: number; jitter: number; pause_ratio: number; speech_rate: number };
  flags: string[];
  latest_utterance: string;
  sbar: {
    situation: string;
    background: string;
    assessment: string;
    recommendation: string;
  };
}

export const OperatorDashboard: React.FC = () => {
  const [queue] = useState<QueueItem[]>([
    {
      id: 'Q-101',
      call_id: 'call_9901_forest',
      caller_number: '+91 94371-XXXXX (Dhenkanal)',
      channel: 'EXOTEL CARRIER (095-138-86363)',
      timestamp: 'Just now (00:42)',
      risk_level: 'CRITICAL',
      svi_score: 0.94,
      emotion: { fear: 0.88, sadness: 0.06, anger: 0.04, neutral: 0.02 },
      acoustic: { pitch_f0: 312, jitter: 0.048, pause_ratio: 0.38, speech_rate: 3.4 },
      flags: ['ACTIVE_PURSUIT', 'WILDERNESS_OUTDOORS', 'ARMED_THREAT'],
      latest_utterance: 'ମୋତେ ମାରିବାକୁ ଗୋଡ଼ାଉଛନ୍ତି, ମୁଁ ଏବେ ଜଙ୍ଗଲରେ ଲୁଚିକି ଅଛି। (Mate maribaku godauchanti...)',
      sbar: {
        situation: 'Caller is being actively chased by armed attackers in a forest.',
        background: 'Caste atrocity incident following land dispute protest in Dhenkanal district.',
        assessment: 'SVI: 0.94 CRITICAL. Acute fear (88%). Spatial wilderness survival instructions active.',
        recommendation: 'Immediate Police PCR 112 intercept to village periphery landmark.'
      }
    },
    {
      id: 'Q-102',
      call_id: 'call_9902_boycott',
      caller_number: '+91 98610-XXXXX (Bargarh)',
      channel: 'WEB-RTC BROWSER',
      timestamp: '3 mins ago',
      risk_level: 'HIGH',
      svi_score: 0.72,
      emotion: { fear: 0.45, sadness: 0.35, anger: 0.15, neutral: 0.05 },
      acoustic: { pitch_f0: 245, jitter: 0.024, pause_ratio: 0.22, speech_rate: 2.8 },
      flags: ['SOCIAL_BOYCOTT', 'WATER_ACCESS_DENIAL', 'KOSLI_DIALECT'],
      latest_utterance: 'ମୋର୍ ପିତା ଖେଡି ଦେଲେ, ପାଣି ନେବାର୍ ମନା କର୍ଲେ। (Mor pita khedi dele...)',
      sbar: {
        situation: 'Family subject to social boycott and denied drinking water access.',
        background: 'Bargarh village committee diktat violating SC/ST PoA Section 3(1)(za).',
        assessment: 'SVI: 0.72 HIGH. Moderate fear and acute vulnerability.',
        recommendation: 'Direct notice to Sub-Divisional Magistrate & District Welfare Officer.'
      }
    }
  ]);

  const [selectedItem, setSelectedItem] = useState<QueueItem>(queue[0]);
  const [dispatchModalOpen, setDispatchModalOpen] = useState(false);
  const [dispatchSuccess, setDispatchSuccess] = useState(false);
  const navigate = useNavigate();

  const handleDispatch = () => {
    setDispatchSuccess(true);
    setTimeout(() => {
      setDispatchModalOpen(false);
      setDispatchSuccess(false);
    }, 2000);
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
                  Live National Operations
                </div>
                <h2 className="h2 max-width-432-mobile-320">Operator Triage Console</h2>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: '#22c55e', display: 'inline-block' }}></span>
                  <span className="regular-m">Exotel &amp; Web Telephony Connected</span>
                </div>
                <button 
                  type="button" 
                  onClick={handleSignOut} 
                  className="button secondary small w-button"
                >
                  Log Out
                </button>
              </div>
            </div>

            {/* Main 2-Column Grid */}
            <div className="w-layout-grid blocks-grid-2-tablet-1-mobile-1" style={{ gridTemplateColumns: '4.5fr 7.5fr' }}>
              {/* Left Column: Active Queue */}
              <div>
                <div className="regular-m margin-bottom-16" style={{ fontWeight: 600 }}>
                  Incoming Priority Queue ({queue.length})
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  {queue.map((item) => (
                    <div
                      key={item.id}
                      onClick={() => setSelectedItem(item)}
                      className="block padding-24-32 bg-grey-3"
                      style={{
                        cursor: 'pointer',
                        border: selectedItem.id === item.id ? '2px solid var(--black)' : '1px solid var(--grey-8)',
                        backgroundColor: selectedItem.id === item.id ? 'var(--white)' : 'var(--grey-3)',
                        transition: 'all 0.2s'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%', marginBottom: '12px' }}>
                        <span className={`triage-badge ${item.risk_level.toLowerCase()}`}>
                          {item.risk_level} • SVI {item.svi_score}
                        </span>
                        <span className="regular-s color-grey-80">{item.timestamp}</span>
                      </div>
                      <h4 className="h4" style={{ fontSize: '20px', marginBottom: '8px' }}>
                        {item.caller_number}
                      </h4>
                      <p className="regular-s color-grey-80">{item.channel}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Right Column: Telemetry & SBAR */}
              <div className="block padding-24-32 bg-grey-3">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', width: '100%', marginBottom: '16px' }}>
                  <div>
                    <span className={`triage-badge ${selectedItem.risk_level.toLowerCase()}`}>
                      {selectedItem.risk_level} RISK
                    </span>
                    <h3 className="h3 margin-bottom-12">{selectedItem.caller_number}</h3>
                    <div className="regular-s color-grey-80">
                      Channel: {selectedItem.channel} • Session Ref: {selectedItem.call_id}
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={() => setDispatchModalOpen(true)}
                    className="button primary w-button"
                    style={{ backgroundColor: '#b91c1c' }}
                  >
                    Dispatch Police 112
                  </button>
                </div>

                <div className="line black margin-bottom-20"></div>

                {/* Verbatim Transcript */}
                <div style={{ width: '100%', marginBottom: '24px' }}>
                  <div className="regular-s color-grey-80 margin-bottom-8" style={{ textTransform: 'uppercase' }}>
                    Latest Verbatim Utterance:
                  </div>
                  <div style={{ backgroundColor: 'var(--white)', border: '1px solid var(--grey-8)', padding: '16px 20px', borderRadius: '4px', fontStyle: 'italic' }}>
                    "{selectedItem.latest_utterance}"
                  </div>
                </div>

                {/* Acoustic & Emotion Telemetry */}
                <div style={{ width: '100%', marginBottom: '24px' }}>
                  <div className="regular-s color-grey-80 margin-bottom-12" style={{ textTransform: 'uppercase' }}>
                    Acoustic &amp; Emotional Distribution Telemetry (Wav2Vec2):
                  </div>
                  <div className="telemetry-row">
                    <span>Acoustic Pitch F0 (Tension / Distress)</span>
                    <span><strong>{selectedItem.acoustic.pitch_f0} Hz</strong></span>
                  </div>
                  <div className="telemetry-row">
                    <span>Vocal Jitter (Micro-Tremor)</span>
                    <span><strong>{selectedItem.acoustic.jitter}</strong></span>
                  </div>
                  <div className="telemetry-row">
                    <span>Speech Pause Ratio (Freeze Defense)</span>
                    <span><strong>{(selectedItem.acoustic.pause_ratio * 100).toFixed(0)}%</strong></span>
                  </div>
                  <div className="telemetry-row">
                    <span>Fear Probability</span>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <div className="telemetry-bar-bg">
                        <div className="telemetry-bar-fill" style={{ width: `${selectedItem.emotion.fear * 100}%`, backgroundColor: '#ef4444' }}></div>
                      </div>
                      <span>{(selectedItem.emotion.fear * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                  <div className="telemetry-row">
                    <span>Sadness Probability</span>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <div className="telemetry-bar-bg">
                        <div className="telemetry-bar-fill" style={{ width: `${selectedItem.emotion.sadness * 100}%`, backgroundColor: '#3b82f6' }}></div>
                      </div>
                      <span>{(selectedItem.emotion.sadness * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                </div>

                {/* SBAR Report */}
                <div style={{ width: '100%' }}>
                  <div className="regular-s color-grey-80 margin-bottom-12" style={{ textTransform: 'uppercase' }}>
                    SBAR Clinical Handoff Report:
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                    <div style={{ backgroundColor: 'var(--white)', border: '1px solid var(--grey-8)', padding: '14px 18px', borderRadius: '4px' }}>
                      <div className="regular-s color-grey-80" style={{ fontWeight: 700 }}>S - SITUATION</div>
                      <p className="regular-m" style={{ fontSize: '14px' }}>{selectedItem.sbar.situation}</p>
                    </div>
                    <div style={{ backgroundColor: 'var(--white)', border: '1px solid var(--grey-8)', padding: '14px 18px', borderRadius: '4px' }}>
                      <div className="regular-s color-grey-80" style={{ fontWeight: 700 }}>B - BACKGROUND</div>
                      <p className="regular-m" style={{ fontSize: '14px' }}>{selectedItem.sbar.background}</p>
                    </div>
                    <div style={{ backgroundColor: 'var(--white)', border: '1px solid var(--grey-8)', padding: '14px 18px', borderRadius: '4px' }}>
                      <div className="regular-s color-grey-80" style={{ fontWeight: 700 }}>A - ASSESSMENT</div>
                      <p className="regular-m" style={{ fontSize: '14px' }}>{selectedItem.sbar.assessment}</p>
                    </div>
                    <div style={{ backgroundColor: 'var(--white)', border: '1px solid var(--grey-8)', padding: '14px 18px', borderRadius: '4px' }}>
                      <div className="regular-s color-grey-80" style={{ fontWeight: 700 }}>R - RECOMMENDATION</div>
                      <p className="regular-m" style={{ fontSize: '14px' }}>{selectedItem.sbar.recommendation}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>
      </section>

      {/* Police 112 Dispatch Modal */}
      {dispatchModalOpen && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h3 className="h3 margin-bottom-16" style={{ color: '#b91c1c' }}>
              Confirm Police PCR 112 Dispatch
            </h3>
            <div className="line black margin-bottom-20"></div>
            <p className="regular-m margin-bottom-20">
              You are dispatching an immediate statutory law-enforcement intercept for:
            </p>
            <div style={{ backgroundColor: 'var(--grey-3)', padding: '16px', borderRadius: '4px', marginBottom: '24px' }}>
              <div><strong>Caller:</strong> {selectedItem.caller_number}</div>
              <div><strong>Assessment:</strong> {selectedItem.sbar.assessment}</div>
              <div><strong>Action:</strong> {selectedItem.sbar.recommendation}</div>
            </div>

            {dispatchSuccess ? (
              <div style={{ color: '#15803d', fontWeight: 700, padding: '12px 0' }}>
                ✓ PCR 112 Unit Dispatched Successfully. Incident Log Transmitted.
              </div>
            ) : (
              <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  onClick={() => setDispatchModalOpen(false)}
                  className="button secondary small w-button"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handleDispatch}
                  className="button primary small w-button"
                  style={{ backgroundColor: '#b91c1c' }}
                >
                  Transmit 112 Dispatch Now
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
};

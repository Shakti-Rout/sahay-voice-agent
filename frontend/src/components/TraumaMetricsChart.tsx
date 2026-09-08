import React from 'react';
import { TrendingUp, AlertTriangle } from 'lucide-react';
import {
  BarChart,
  Bar,
  Cell,
  CartesianGrid,
  LabelList,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

export interface TraumaIndicatorData {
  indicator: string;
  score: number;
  category: string;
  color: string;
}

interface TraumaMetricsChartProps {
  callerId: string;
  callerNumber: string;
  riskLevel: 'CRITICAL' | 'HIGH' | 'LOW';
  sviScore: number;
  data: TraumaIndicatorData[];
}

export const TraumaMetricsChart: React.FC<TraumaMetricsChartProps> = ({
  callerNumber,
  riskLevel,
  sviScore,
  data,
}) => {
  return (
    <div
      style={{
        backgroundColor: '#ffffff',
        border: '1px solid var(--grey-8, #e5e7eb)',
        borderRadius: '6px',
        padding: '20px',
        marginBottom: '24px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
      }}
    >
      {/* Header */}
      <div style={{ marginBottom: '16px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h4
            style={{
              fontSize: '16px',
              fontWeight: 700,
              margin: 0,
              color: '#111827',
              letterSpacing: '-0.01em',
            }}
          >
            PS 26093 Trauma &amp; Distress Indicators
          </h4>
          <span
            style={{
              fontSize: '11px',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              padding: '3px 8px',
              borderRadius: '4px',
              backgroundColor: riskLevel === 'CRITICAL' ? '#fee2e2' : '#fef3c7',
              color: riskLevel === 'CRITICAL' ? '#991b1b' : '#92400e',
            }}
          >
            SVI {(sviScore * 100).toFixed(0)}% • {riskLevel}
          </span>
        </div>
        <p style={{ fontSize: '13px', color: '#6b7280', margin: '4px 0 0 0' }}>
          Calibrated acoustic prosody, linguistic threats &amp; emotional telemetry for {callerNumber}
        </p>
      </div>

      {/* Chart */}
      <div style={{ width: '100%', height: 340 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            layout="vertical"
            margin={{
              top: 6,
              right: 48,
              bottom: 6,
              left: 4,
            }}
            barCategoryGap={6}
          >
            <CartesianGrid horizontal={false} stroke="#f3f4f6" />
            <YAxis
              dataKey="indicator"
              type="category"
              tickLine={false}
              axisLine={false}
              hide
            />
            <XAxis dataKey="score" type="number" domain={[0, 100]} hide />
            <Tooltip
              cursor={{ fill: 'rgba(0, 0, 0, 0.03)' }}
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const item = payload[0].payload as TraumaIndicatorData;
                  return (
                    <div
                      style={{
                        backgroundColor: '#111827',
                        color: '#ffffff',
                        padding: '8px 12px',
                        borderRadius: '6px',
                        fontSize: '12px',
                        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                      }}
                    >
                      <div style={{ fontWeight: 700 }}>{item.indicator}</div>
                      <div style={{ color: '#9ca3af', fontSize: '11px', marginTop: '2px' }}>
                        Category: {item.category}
                      </div>
                      <div style={{ color: item.color, fontWeight: 700, marginTop: '4px', fontSize: '13px' }}>
                        Distress Score: {item.score}%
                      </div>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Bar
              dataKey="score"
              fill="#dc2626"
              radius={[0, 4, 4, 0]}
              barSize={24}
              isAnimationActive={false}
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
              <LabelList
                dataKey="indicator"
                position="insideLeft"
                offset={10}
                fill="#ffffff"
                fontSize={11}
                fontWeight={600}
                style={{ pointerEvents: 'none' }}
              />
              <LabelList
                dataKey="score"
                position="right"
                offset={8}
                fill="#111827"
                fontSize={12}
                fontWeight={700}
                formatter={(val: unknown) => `${val}%`}
              />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Footer */}
      <div
        style={{
          borderTop: '1px solid #f3f4f6',
          paddingTop: '12px',
          marginTop: '8px',
          display: 'flex',
          flexDirection: 'column',
          gap: '4px',
          fontSize: '13px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 600, color: '#111827' }}>
          <TrendingUp style={{ width: '16px', height: '16px', color: '#dc2626' }} />
          <span>Elevated multi-modal distress response detected across 8 PS 26093 indicators</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', color: '#6b7280' }}>
          <AlertTriangle style={{ width: '14px', height: '14px', color: '#f59e0b' }} />
          <span>Automated SBAR generated for PCR 112 police intercept &amp; DLSA legal notice</span>
        </div>
      </div>
    </div>
  );
};

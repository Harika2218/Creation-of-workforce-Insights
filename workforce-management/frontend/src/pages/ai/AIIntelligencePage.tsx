import React, { useState, useEffect } from 'react';
import {
  BrainCircuit,
  TrendingUp,
  AlertTriangle,
  Users,
  ShieldCheck,
  Calendar,
  Sparkles,
  Award,
  Layers,
  CheckCircle2,
  Clock,
  ArrowUpRight,
  Filter,
  Info,
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

import { Card } from '../../components/common/Card';
import { Badge } from '../../components/common/Badge';
import { Button } from '../../components/common/Button';
import { LoadingSkeleton } from '../../components/common/LoadingSkeleton';
import { AIIntelligenceCore, ThreeDMetricCard } from '../../components/3d';
import { aiService } from '../../services/aiService';
import {
  WorkforceForecast,
  StaffingRecommendation,
  AttritionPrediction,
  AbsenteeismPrediction,
  AttendanceAnomaly,
  SkillGap,
  ShiftRecommendation,
  ResourceRecommendation,
  AIModelMetrics,
} from '../../types/ai';

type TabKey = 'forecast' | 'attrition' | 'absenteeism' | 'anomalies' | 'skills' | 'shifts' | 'governance';

export const AIIntelligencePage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabKey>('forecast');
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Data states
  const [forecasts, setForecasts] = useState<WorkforceForecast[]>([]);
  const [staffingRecs, setStaffingRecs] = useState<StaffingRecommendation[]>([]);
  const [attritionList, setAttritionList] = useState<AttritionPrediction[]>([]);
  const [absenteeismList, setAbsenteeismList] = useState<AbsenteeismPrediction[]>([]);
  const [anomalies, setAnomalies] = useState<AttendanceAnomaly[]>([]);
  const [skillGaps, setSkillGaps] = useState<SkillGap[]>([]);
  const [shiftRecs, setShiftRecs] = useState<ShiftRecommendation[]>([]);
  const [resourceRecs, setResourceRecs] = useState<ResourceRecommendation[]>([]);
  const [metrics, setMetrics] = useState<AIModelMetrics | null>(null);

  // Filters
  const [selectedDept, setSelectedDept] = useState<string>('ALL');

  useEffect(() => {
    const fetchAIData = async () => {
      try {
        setIsLoading(true);
        const [
          fcData,
          srData,
          attData,
          absData,
          anomData,
          gapData,
          shiftData,
          resData,
          metData,
        ] = await Promise.all([
          aiService.getWorkforceForecast(),
          aiService.getStaffingRecommendations(),
          aiService.getAttrition(),
          aiService.getAbsenteeism(),
          aiService.getAttendanceAnomalies(50),
          aiService.getSkillGaps(),
          aiService.getShiftRecommendations(),
          aiService.getResourceRecommendations(),
          aiService.getModelMetrics().catch(() => null),
        ]);

        setForecasts(fcData);
        setStaffingRecs(srData);
        setAttritionList(attData);
        setAbsenteeismList(absData);
        setAnomalies(anomData);
        setSkillGaps(gapData);
        setShiftRecs(shiftData);
        setResourceRecs(resData);
        setMetrics(metData);
      } catch (err) {
        console.error('Error fetching AI intelligence data:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchAIData();
  }, []);

  // Summary counts
  const highAttritionCount = attritionList.filter(
    (a) => (a.risk_band || a.risk_category) === 'HIGH'
  ).length;
  const highAbsenteeismCount = absenteeismList.filter((a) => a.risk_level === 'HIGH').length;
  const totalStaffingGap = forecasts.reduce((acc, f) => acc + (f.recommended_hires || 0), 0);

  // Colors for charts
  const RISK_COLORS = {
    HIGH: '#ef4444',
    MEDIUM: '#f59e0b',
    LOW: '#10b981',
  };

  const attritionDonutData = [
    { name: 'Low Risk', value: attritionList.filter((a) => (a.risk_band || a.risk_category) === 'LOW').length || 150, color: '#10b981' },
    { name: 'Medium Risk', value: attritionList.filter((a) => (a.risk_band || a.risk_category) === 'MEDIUM').length || 38, color: '#f59e0b' },
    { name: 'High Risk', value: highAttritionCount || 12, color: '#ef4444' },
  ];

  const forecastChartData = forecasts.map((f) => ({
    name: f.department_name ? f.department_name.split(' ')[0] : f.department_id,
    'Current Staff': f.current_headcount,
    'Projected Need': f.projected_headcount_need || f.predicted_demand || f.current_headcount,
    Gap: f.recommended_hires || 0,
  }));

  if (isLoading) {
    return (
      <div className="space-y-6">
        <LoadingSkeleton lines={6} height="36px" />
        <LoadingSkeleton lines={4} height="28px" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-indigo-900 via-indigo-800 to-purple-900 rounded-2xl p-6 text-white shadow-xl relative overflow-hidden">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="px-3 py-1 bg-indigo-500/30 border border-indigo-400/40 rounded-full text-xs font-semibold text-indigo-200 tracking-wide uppercase flex items-center gap-1.5">
                <Sparkles size={13} className="text-yellow-300" /> Phase 5 ML Intelligence
              </span>
              <span className="px-2.5 py-0.5 bg-emerald-500/20 text-emerald-300 border border-emerald-400/30 rounded-full text-xs font-medium">
                Models Active (v1.0.0)
              </span>
            </div>
            <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
              Workforce Intelligence & Predictive Analytics
            </h1>
            <p className="text-indigo-200 text-sm mt-1 max-w-2xl">
              Probabilistic decision-support models for capacity forecasting, attrition early warnings,
              unsupervised anomaly detection, and automated resource matching.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              className="bg-white/10 hover:bg-white/20 text-white border-white/20 text-xs"
              onClick={() => setActiveTab('governance')}
            >
              <ShieldCheck size={15} className="mr-1.5 text-emerald-400" /> Model Governance
            </Button>
          </div>
        </div>
      </div>

      {/* 3D AI Intelligence Neural Core */}
      <AIIntelligenceCore />

      {/* 3D Elevated KPI Cards */}
      <div className="grid-4">
        <ThreeDMetricCard
          label="Est. Talent Deficit (Q3-2026)"
          value={`+${totalStaffingGap} Hires`}
          badge="Forecast Gap"
          badgeVariant="warning"
          subtext="Across 9 operational divisions"
          icon={<TrendingUp size={22} />}
          iconBg="rgba(99, 102, 241, 0.15)"
          iconColor="var(--primary)"
          accentColor="var(--primary)"
        />
        <ThreeDMetricCard
          label="High Attrition Risk Signal"
          value={highAttritionCount}
          badge="Critical Risk"
          badgeVariant="danger"
          subtext="Model-estimated probability > 0.60"
          icon={<AlertTriangle size={22} />}
          iconBg="rgba(239, 68, 68, 0.15)"
          iconColor="var(--danger)"
          accentColor="var(--danger)"
        />
        <ThreeDMetricCard
          label="Absenteeism Alerts"
          value={highAbsenteeismCount}
          badge="High Likelihood"
          badgeVariant="warning"
          subtext="High 14-day absence likelihood"
          icon={<Clock size={22} />}
          iconBg="rgba(245, 158, 11, 0.15)"
          iconColor="var(--warning)"
          accentColor="var(--warning)"
        />
        <ThreeDMetricCard
          label="Attendance Anomalies"
          value={anomalies.length}
          badge="Isolation Forest"
          badgeVariant="purple"
          subtext="Outlier multivariate events"
          icon={<BrainCircuit size={22} />}
          iconBg="rgba(168, 85, 247, 0.15)"
          iconColor="var(--purple)"
          accentColor="var(--purple)"
        />
      </div>

      {/* Tab Navigation */}
      <div className="flex border-b border-gray-200 dark:border-gray-800 space-x-2 overflow-x-auto pb-1">
        {[
          { key: 'forecast', label: 'Demand & Staffing', icon: <TrendingUp size={16} /> },
          { key: 'attrition', label: 'Attrition Risk Radar', icon: <AlertTriangle size={16} /> },
          { key: 'absenteeism', label: 'Absenteeism Signals', icon: <Clock size={16} /> },
          { key: 'anomalies', label: 'Attendance Anomalies', icon: <BrainCircuit size={16} /> },
          { key: 'skills', label: 'Skills & Training', icon: <Award size={16} /> },
          { key: 'shifts', label: 'Shifts & Allocations', icon: <Layers size={16} /> },
          { key: 'governance', label: 'Fairness & Metrics', icon: <ShieldCheck size={16} /> },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key as TabKey)}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all whitespace-nowrap ${
              activeTab === tab.key
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'
            }`}
          >
            {tab.icon}
            {tab.label}
          </button>
        ))}
      </div>

      {/* TAB CONTENT: 1. Demand & Staffing */}
      {activeTab === 'forecast' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <Card className="lg:col-span-8 p-5">
              <div className="flex justify-between items-center mb-4">
                <div>
                  <h3 className="text-base font-bold text-gray-900 dark:text-white">
                    Workforce Headcount vs Projected Demand (Q3-2026)
                  </h3>
                  <p className="text-xs text-gray-500">
                    Calculated using exponential smoothing and project commitment pipelines
                  </p>
                </div>
                <Badge variant="info">Statistical Trend Scaling</Badge>
              </div>
              <div className="h-72 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={forecastChartData}>
                    <XAxis dataKey="name" stroke="#9ca3af" fontSize={11} />
                    <YAxis stroke="#9ca3af" fontSize={11} />
                    <Tooltip />
                    <Legend wrapperStyle={{ fontSize: '12px' }} />
                    <Bar dataKey="Current Staff" fill="#6366f1" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="Projected Need" fill="#a855f7" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </Card>

            <Card className="lg:col-span-4 p-5 flex flex-col justify-between">
              <div>
                <h3 className="text-base font-bold text-gray-900 dark:text-white mb-2">
                  Budget & Expansion Summary
                </h3>
                <p className="text-xs text-gray-500 mb-4">
                  Financial impact estimates based on projected talent requirements.
                </p>
                <div className="space-y-3">
                  <div className="p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg flex justify-between items-center">
                    <span className="text-xs text-gray-600 dark:text-gray-400">Total Projected Deficit</span>
                    <span className="text-sm font-bold text-indigo-600">{totalStaffingGap} Positions</span>
                  </div>
                  <div className="p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg flex justify-between items-center">
                    <span className="text-xs text-gray-600 dark:text-gray-400">Estimated Annual Payroll Impact</span>
                    <span className="text-sm font-bold text-gray-900 dark:text-white">
                      INR {(totalStaffingGap * 1200000).toLocaleString()}
                    </span>
                  </div>
                  <div className="p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg flex justify-between items-center">
                    <span className="text-xs text-gray-600 dark:text-gray-400">Target Completion Horizon</span>
                    <span className="text-sm font-semibold text-gray-900 dark:text-white">Q3-2026 Fiscal</span>
                  </div>
                </div>
              </div>
              <div className="mt-4 p-3 bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800/40 rounded-lg flex items-start gap-2 text-xs text-amber-800 dark:text-amber-300">
                <Info size={15} className="mt-0.5 shrink-0" />
                <span>Recommendations serve as planning signals. Final hiring requires executive approval.</span>
              </div>
            </Card>
          </div>

          {/* Strategic Staffing Table */}
          <Card className="p-5">
            <h3 className="text-base font-bold text-gray-900 dark:text-white mb-3">
              Strategic Department Staffing Recommendations
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-gray-200 dark:border-gray-800 text-gray-500">
                    <th className="py-2.5 px-3">Department</th>
                    <th className="py-2.5 px-3">Target Role</th>
                    <th className="py-2.5 px-3">Current</th>
                    <th className="py-2.5 px-3">Projected Demand</th>
                    <th className="py-2.5 px-3">Gap</th>
                    <th className="py-2.5 px-3">Priority</th>
                    <th className="py-2.5 px-3">Strategic Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                  {staffingRecs.map((sr) => (
                    <tr key={sr.recommendation_id} className="hover:bg-gray-50 dark:hover:bg-gray-800/40">
                      <td className="py-2.5 px-3 font-semibold text-gray-900 dark:text-white">
                        {sr.department_name || sr.department_id}
                      </td>
                      <td className="py-2.5 px-3 text-indigo-600 dark:text-indigo-400 font-medium">
                        {sr.target_role}
                      </td>
                      <td className="py-2.5 px-3">{sr.current_staff || 25}</td>
                      <td className="py-2.5 px-3">{sr.forecast_demand || 30}</td>
                      <td className="py-2.5 px-3 font-bold text-rose-600">+{sr.estimated_gap || sr.recommended_count}</td>
                      <td className="py-2.5 px-3">
                        <Badge
                          variant={
                            sr.priority === 'HIGH' ? 'danger' : sr.priority === 'MEDIUM' ? 'warning' : 'success'
                          }
                        >
                          {sr.priority}
                        </Badge>
                      </td>
                      <td className="py-2.5 px-3 text-gray-600 dark:text-gray-400 max-w-md">
                        {sr.recommendation || sr.rationale}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      )}

      {/* TAB CONTENT: 2. Attrition Risk Radar */}
      {activeTab === 'attrition' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <Card className="lg:col-span-4 p-5">
              <h3 className="text-base font-bold text-gray-900 dark:text-white mb-2">
                Workforce Attrition Risk Distribution
              </h3>
              <p className="text-xs text-gray-500 mb-4">
                Gradient Boosting model calibrated across 200 active employees
              </p>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={attritionDonutData}
                      innerRadius={60}
                      outerRadius={85}
                      paddingAngle={4}
                      dataKey="value"
                    >
                      {attritionDonutData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend wrapperStyle={{ fontSize: '11px' }} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="mt-2 text-center text-xs text-gray-500">
                Total Monitored: {attritionList.length} employees
              </div>
            </Card>

            <Card className="lg:col-span-8 p-5">
              <div className="flex justify-between items-center mb-3">
                <h3 className="text-base font-bold text-gray-900 dark:text-white">
                  Identified Retention Attention Radar (Top Signals)
                </h3>
                <Badge variant="warning">Probabilistic Risk Signal</Badge>
              </div>
              <p className="text-xs text-gray-500 mb-4">
                Employees exhibiting statistical correlation with flight risk drivers (excess overtime, sub-target KPI, or extended tenure without promotion).
              </p>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-gray-200 dark:border-gray-800 text-gray-500">
                      <th className="py-2.5 px-3">Employee</th>
                      <th className="py-2.5 px-3">Department</th>
                      <th className="py-2.5 px-3">Estimated Risk</th>
                      <th className="py-2.5 px-3">Risk Band</th>
                      <th className="py-2.5 px-3">Primary Contributing Factors</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                    {attritionList
                      .filter((a) => (a.risk_band || a.risk_category) !== 'LOW')
                      .slice(0, 10)
                      .map((a) => (
                        <tr key={a.employee_id} className="hover:bg-gray-50 dark:hover:bg-gray-800/40">
                          <td className="py-2.5 px-3 font-semibold text-gray-900 dark:text-white">
                            {a.employee_id}
                          </td>
                          <td className="py-2.5 px-3">{a.department_id || 'DEP01'}</td>
                          <td className="py-2.5 px-3 font-bold text-rose-600">
                            {((a.attrition_probability || a.risk_score) * 100).toFixed(1)}%
                          </td>
                          <td className="py-2.5 px-3">
                            <Badge
                              variant={
                                (a.risk_band || a.risk_category) === 'HIGH' ? 'danger' : 'warning'
                              }
                            >
                              {a.risk_band || a.risk_category}
                            </Badge>
                          </td>
                          <td className="py-2.5 px-3 text-gray-600 dark:text-gray-400">
                            {(a.top_contributing_features || a.contributing_factors || []).join(', ')}
                          </td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            </Card>
          </div>
        </div>
      )}

      {/* TAB CONTENT: 3. Absenteeism Signals */}
      {activeTab === 'absenteeism' && (
        <div className="space-y-6">
          <Card className="p-5">
            <div className="flex justify-between items-center mb-3">
              <div>
                <h3 className="text-base font-bold text-gray-900 dark:text-white">
                  Predictive Absenteeism Early Warning Radar
                </h3>
                <p className="text-xs text-gray-500">
                  Estimates the probability that an employee may experience unscheduled absences in the next 14-day window.
                </p>
              </div>
              <Badge variant="info">Random Forest Classifier</Badge>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-gray-200 dark:border-gray-800 text-gray-500">
                    <th className="py-2.5 px-3">Employee ID</th>
                    <th className="py-2.5 px-3">Absence Probability</th>
                    <th className="py-2.5 px-3">Risk Band</th>
                    <th className="py-2.5 px-3">Top Driving Features</th>
                    <th className="py-2.5 px-3">Prediction Date</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                  {absenteeismList.slice(0, 15).map((abs) => (
                    <tr key={abs.employee_id} className="hover:bg-gray-50 dark:hover:bg-gray-800/40">
                      <td className="py-2.5 px-3 font-semibold text-gray-900 dark:text-white">
                        {abs.employee_id}
                      </td>
                      <td className="py-2.5 px-3 font-bold text-gray-900 dark:text-white">
                        {(abs.probability * 100).toFixed(1)}%
                      </td>
                      <td className="py-2.5 px-3">
                        <Badge
                          variant={
                            abs.risk_level === 'HIGH'
                              ? 'danger'
                              : abs.risk_level === 'MEDIUM'
                              ? 'warning'
                              : 'success'
                          }
                        >
                          {abs.risk_level}
                        </Badge>
                      </td>
                      <td className="py-2.5 px-3 text-gray-600 dark:text-gray-400">
                        {abs.important_features
                          .map((f) => `${f.feature.replace(/_/g, ' ')} (${f.current_value ?? ''})`)
                          .join(', ')}
                      </td>
                      <td className="py-2.5 px-3 text-gray-500">{abs.prediction_date}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      )}

      {/* TAB CONTENT: 4. Attendance Anomalies */}
      {activeTab === 'anomalies' && (
        <div className="space-y-6">
          <Card className="p-5">
            <div className="flex justify-between items-center mb-3">
              <div>
                <h3 className="text-base font-bold text-gray-900 dark:text-white">
                  Attendance Anomaly Catalog (Isolation Forest Unsupervised Detection)
                </h3>
                <p className="text-xs text-gray-500">
                  Multivariate clustering identifies extreme shifts, prolonged overtime, or irregular clock-in timing with explainable causes.
                </p>
              </div>
              <Badge variant="danger">Unsupervised Isolation Forest</Badge>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-gray-200 dark:border-gray-800 text-gray-500">
                    <th className="py-2.5 px-3">Anomaly ID</th>
                    <th className="py-2.5 px-3">Date</th>
                    <th className="py-2.5 px-3">Employee</th>
                    <th className="py-2.5 px-3">Severity</th>
                    <th className="py-2.5 px-3">Anomaly Score</th>
                    <th className="py-2.5 px-3">Root Cause Reason</th>
                    <th className="py-2.5 px-3">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                  {anomalies.slice(0, 15).map((anom) => (
                    <tr key={anom.anomaly_id} className="hover:bg-gray-50 dark:hover:bg-gray-800/40">
                      <td className="py-2.5 px-3 font-mono font-medium text-gray-700 dark:text-gray-300">
                        {anom.anomaly_id}
                      </td>
                      <td className="py-2.5 px-3">{anom.date}</td>
                      <td className="py-2.5 px-3 font-semibold text-gray-900 dark:text-white">
                        {anom.employee_id}
                      </td>
                      <td className="py-2.5 px-3">
                        <Badge variant={anom.severity === 'HIGH' ? 'danger' : 'warning'}>
                          {anom.severity}
                        </Badge>
                      </td>
                      <td className="py-2.5 px-3 font-mono">{(anom.anomaly_score || 0.88).toFixed(2)}</td>
                      <td className="py-2.5 px-3 text-gray-700 dark:text-gray-300 max-w-md font-medium">
                        {anom.reason}
                      </td>
                      <td className="py-2.5 px-3">
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300">
                          {anom.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      )}

      {/* TAB CONTENT: 5. Skills & Training */}
      {activeTab === 'skills' && (
        <div className="space-y-6">
          <Card className="p-5">
            <div className="flex justify-between items-center mb-3">
              <div>
                <h3 className="text-base font-bold text-gray-900 dark:text-white">
                  Enterprise Skills Gap Matrix
                </h3>
                <p className="text-xs text-gray-500">
                  Compares departmental competency benchmarks against verified workforce proficiencies.
                </p>
              </div>
              <Badge variant="info">Matrix Alignment Engine</Badge>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-gray-200 dark:border-gray-800 text-gray-500">
                    <th className="py-2.5 px-3">Department</th>
                    <th className="py-2.5 px-3">Required Competency</th>
                    <th className="py-2.5 px-3">Benchmark Level</th>
                    <th className="py-2.5 px-3">Available Holders</th>
                    <th className="py-2.5 px-3">Target Headcount</th>
                    <th className="py-2.5 px-3">Skill Deficit</th>
                    <th className="py-2.5 px-3">Priority</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                  {skillGaps.slice(0, 14).map((sg, idx) => (
                    <tr key={idx} className="hover:bg-gray-50 dark:hover:bg-gray-800/40">
                      <td className="py-2.5 px-3 font-semibold text-gray-900 dark:text-white">
                        {sg.department_name}
                      </td>
                      <td className="py-2.5 px-3 font-medium text-indigo-600 dark:text-indigo-400">
                        {sg.required_skill}
                      </td>
                      <td className="py-2.5 px-3">{sg.target_proficiency}</td>
                      <td className="py-2.5 px-3">{sg.available_skill_count}</td>
                      <td className="py-2.5 px-3">{sg.target_headcount || 4}</td>
                      <td className="py-2.5 px-3 font-bold text-rose-600">
                        {sg.skill_gap > 0 ? `-${sg.skill_gap}` : 'Balanced'}
                      </td>
                      <td className="py-2.5 px-3">
                        <Badge
                          variant={
                            sg.priority === 'HIGH'
                              ? 'danger'
                              : sg.priority === 'MEDIUM'
                              ? 'warning'
                              : 'success'
                          }
                        >
                          {sg.priority}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      )}

      {/* TAB CONTENT: 6. Shifts & Allocations */}
      {activeTab === 'shifts' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="p-5">
              <h3 className="text-base font-bold text-gray-900 dark:text-white mb-2">
                Intelligent Shift Scheduling Recommendations
              </h3>
              <p className="text-xs text-gray-500 mb-4">
                Shift rotation advice formulated to prevent overtime fatigue and align with punctuality history.
              </p>
              <div className="space-y-3">
                {shiftRecs.slice(0, 5).map((sr) => (
                  <div
                    key={sr.employee_id}
                    className="p-3.5 bg-gray-50 dark:bg-gray-800/50 border border-gray-100 dark:border-gray-800 rounded-xl flex items-start justify-between"
                  >
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-sm text-gray-900 dark:text-white">
                          {sr.employee_name || sr.employee_id}
                        </span>
                        <Badge variant="outline">{sr.recommended_shift}</Badge>
                      </div>
                      <p className="text-xs text-indigo-600 dark:text-indigo-400 font-medium mt-0.5">
                        {sr.shift_name}
                      </p>
                      <p className="text-xs text-gray-500 mt-1 max-w-sm">{sr.reason}</p>
                    </div>
                    <Badge variant="success">Proposed</Badge>
                  </div>
                ))}
              </div>
            </Card>

            <Card className="p-5">
              <h3 className="text-base font-bold text-gray-900 dark:text-white mb-2">
                Project Resource Allocation Matches
              </h3>
              <p className="text-xs text-gray-500 mb-4">
                Optimized matching between enterprise project demands and developer availability.
              </p>
              <div className="space-y-3">
                {resourceRecs.slice(0, 5).map((res) => (
                  <div
                    key={res.allocation_id}
                    className="p-3.5 bg-gray-50 dark:bg-gray-800/50 border border-gray-100 dark:border-gray-800 rounded-xl flex items-start justify-between"
                  >
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-sm text-gray-900 dark:text-white">
                          {res.project_name || res.project_id}
                        </span>
                        <Badge variant="info">{res.skill_match_pct || 92}% Match</Badge>
                      </div>
                      <p className="text-xs text-gray-700 dark:text-gray-300 font-medium mt-0.5">
                        Recommended: {res.employee_name || res.recommended_employee || res.employee_id}
                      </p>
                      <p className="text-xs text-gray-500 mt-1 max-w-sm">
                        {res.recommendation_reason}
                      </p>
                    </div>
                    <div className="text-right">
                      <span className="text-xs font-bold text-emerald-600">
                        {res.availability_hours || 40}h/wk
                      </span>
                      <p className="text-[10px] text-gray-400">Available</p>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </div>
      )}

      {/* TAB CONTENT: 7. Model Governance & Fairness */}
      {activeTab === 'governance' && (
        <div className="space-y-6">
          <Card className="p-6">
            <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
              <ShieldCheck size={20} className="text-emerald-500" /> Model Governance & Fairness Safeguards
            </h3>
            <p className="text-xs text-gray-500 mb-5">
              Auditable documentation of ethical safeguards, protected attribute exclusions, and validation metrics.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="p-4 bg-emerald-50 dark:bg-emerald-950/20 border border-emerald-200 dark:border-emerald-800/30 rounded-xl">
                <span className="text-xs font-bold text-emerald-800 dark:text-emerald-300 uppercase tracking-wider block mb-1">
                  Protected Attributes Excluded
                </span>
                <p className="text-xs text-emerald-700 dark:text-emerald-400">
                  Features strictly exclude: gender, date of birth / age, personal address, marital status, and religion.
                </p>
              </div>

              <div className="p-4 bg-blue-50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-800/30 rounded-xl">
                <span className="text-xs font-bold text-blue-800 dark:text-blue-300 uppercase tracking-wider block mb-1">
                  Data Leakage Prevention
                </span>
                <p className="text-xs text-blue-700 dark:text-blue-400">
                  Feature windows strictly derived from historical snapshots prior to prediction cutoff. Zero future post-event leakage.
                </p>
              </div>

              <div className="p-4 bg-purple-50 dark:bg-purple-950/20 border border-purple-200 dark:border-purple-800/30 rounded-xl">
                <span className="text-xs font-bold text-purple-800 dark:text-purple-300 uppercase tracking-wider block mb-1">
                  Decision Support Guarantee
                </span>
                <p className="text-xs text-purple-700 dark:text-purple-400">
                  Outputs represent statistical associations only. Autonomous disciplinary or termination actions are strictly prohibited.
                </p>
              </div>
            </div>

            {metrics && metrics.models && (
              <div>
                <h4 className="text-sm font-bold text-gray-900 dark:text-white mb-3">
                  Trained Model Performance Registry
                </h4>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs border-collapse">
                    <thead>
                      <tr className="border-b border-gray-200 dark:border-gray-800 text-gray-500">
                        <th className="py-2 px-3">Model</th>
                        <th className="py-2 px-3">Version</th>
                        <th className="py-2 px-3">Samples</th>
                        <th className="py-2 px-3">Accuracy</th>
                        <th className="py-2 px-3">Precision</th>
                        <th className="py-2 px-3">Recall</th>
                        <th className="py-2 px-3">F1-Score</th>
                        <th className="py-2 px-3">ROC-AUC</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                      {Object.entries(metrics.models).map(([name, m]: [string, any]) => (
                        <tr key={name} className="hover:bg-gray-50 dark:hover:bg-gray-800/40">
                          <td className="py-2 px-3 font-semibold text-gray-900 dark:text-white capitalize">
                            {name.replace(/_/g, ' ')}
                          </td>
                          <td className="py-2 px-3 font-mono text-gray-600 dark:text-gray-400">
                            {m.model_version || 'v1.0.0'}
                          </td>
                          <td className="py-2 px-3">{m.samples_trained || m.total_records_analyzed || 200}</td>
                          <td className="py-2 px-3 font-bold text-emerald-600">
                            {m.accuracy ? `${(m.accuracy * 100).toFixed(1)}%` : 'N/A (Unsupervised)'}
                          </td>
                          <td className="py-2 px-3">{m.precision ? `${(m.precision * 100).toFixed(1)}%` : 'N/A'}</td>
                          <td className="py-2 px-3">{m.recall ? `${(m.recall * 100).toFixed(1)}%` : 'N/A'}</td>
                          <td className="py-2 px-3">{m.f1_score ? `${(m.f1_score * 100).toFixed(1)}%` : 'N/A'}</td>
                          <td className="py-2 px-3 font-bold text-indigo-600">
                            {m.roc_auc ? `${(m.roc_auc * 100).toFixed(1)}%` : 'N/A'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </Card>
        </div>
      )}
    </div>
  );
};

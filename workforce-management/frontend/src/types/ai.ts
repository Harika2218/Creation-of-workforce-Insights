/**
 * TypeScript Interfaces for AI Workforce Intelligence
 */

export interface FeatureImportance {
  feature: string;
  importance: number;
  current_value?: any;
}

export interface AbsenteeismPrediction {
  employee_id: string;
  prediction: number;
  probability: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  important_features: FeatureImportance[];
  prediction_date: string;
  model_version: string;
  disclaimer: string;
}

export interface AttritionPrediction {
  prediction_id?: string;
  employee_id: string;
  department_id?: string;
  attrition_probability?: number;
  risk_score: number;
  risk_band?: 'LOW' | 'MEDIUM' | 'HIGH';
  risk_category?: string;
  top_contributing_features?: string[];
  contributing_factors?: string[];
  prediction_date?: string;
  last_evaluated?: string;
  model_version: string;
  disclaimer: string;
}

export interface AttendanceAnomaly {
  anomaly_id: string;
  attendance_id: string;
  employee_id: string;
  date: string;
  anomaly_score: number;
  is_anomaly: boolean;
  anomaly_type?: string;
  reason: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH';
  status: string;
  detected_at?: string;
  model_version?: string;
}

export interface ProductivityScoreComponents {
  kpi_achievement: number;
  goal_completion: number;
  billable_efficiency: number;
  attendance_reliability: number;
}

export interface ProductivityEvaluation {
  employee_id: string;
  productivity_score: number;
  score_components: ProductivityScoreComponents;
  period: string;
  model_version: string;
  explanation: string;
}

export interface WorkforceForecast {
  forecast_id: string;
  department_id: string;
  department_name?: string;
  forecast_period: string;
  current_headcount: number;
  projected_headcount_need: number;
  predicted_demand?: number;
  lower_bound?: number;
  upper_bound?: number;
  recommended_hires: number;
  estimated_gap?: number;
  budget_impact: number;
  status: string;
  model_version: string;
}

export interface StaffingRecommendation {
  recommendation_id: string;
  department_id: string;
  department_name?: string;
  target_role: string;
  current_staff?: number;
  forecast_demand?: number;
  estimated_gap?: number;
  recommended_count: number;
  priority: 'LOW' | 'MEDIUM' | 'HIGH';
  recommendation?: string;
  rationale: string;
  model_version: string;
}

export interface SkillGap {
  department_id: string;
  department_name: string;
  role: string;
  required_skill: string;
  target_proficiency: string;
  available_skill_count: number;
  target_headcount?: number;
  skill_gap: number;
  priority: 'LOW' | 'MEDIUM' | 'HIGH';
  model_version: string;
}

export interface TrainingRecommendation {
  employee_id: string;
  skill: string;
  current_proficiency: string;
  target_proficiency: string;
  recommended_training: string;
  program_id?: string;
  duration_hours?: number;
  reason: string;
  model_version: string;
}

export interface ShiftRecommendation {
  employee_id: string;
  employee_name?: string;
  department_id?: string;
  recommended_shift: string;
  shift_name: string;
  reason: string;
  expected_overtime: string;
  skill_match: string;
  status?: string;
  model_version: string;
}

export interface ResourceRecommendation {
  allocation_id: string;
  project_id: string;
  project_name?: string;
  recommended_employee?: string;
  employee_id?: string;
  employee_name?: string;
  skill_match_pct?: number;
  availability_hours?: number;
  current_workload_hours?: number;
  recommendation_reason?: string;
  status?: string;
  model_version: string;
}

export interface AIModelMetrics {
  system: string;
  version: string;
  evaluated_at: string;
  fairness_safeguards: {
    protected_attributes_excluded: string[];
    data_leakage_checks: string;
    decision_support_principle: string;
  };
  models: Record<string, any>;
}

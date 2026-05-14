"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import KPICard from "./KPICard";
import ChartCard from "./ChartCard";
import { useAuth } from "@/lib/auth-context";
import { analyticsAPI } from "@/lib/api";

// Demo data fallback for when the backend is not running
const DEMO_KPIS = {
  total_encounters: 101766,
  unique_patients: 71518,
  readmission_rate_30day: 11.23,
  readmission_rate_any: 46.19,
  avg_time_in_hospital: 4.4,
  avg_num_medications: 16.02,
  avg_num_procedures: 1.34,
  avg_lab_procedures: 43.1,
  avg_diagnoses: 7.42,
  emergency_rate: 53.89,
  diabetes_med_rate: 78.36,
  insulin_usage_rate: 53.76,
};

const DEMO_CHARTS = {
  readmission_distribution: { type: "donut", data: { "NO": 54864, ">30": 35545, "<30": 11357 } },
  age_distribution: { type: "bar", data: { "[50-60)": 17838, "[60-70)": 18784, "[70-80)": 22697, "[80-90)": 15680, "[40-50)": 12547, "[30-40)": 6943, "[20-30)": 4180, "[10-20)": 1375, "[0-10)": 838, "[90-100)": 1584 } },
  gender_distribution: { type: "pie", data: { "Female": 54708, "Male": 47055, "Unknown/Invalid": 3 } },
  race_distribution: { type: "bar", data: { "Caucasian": 76099, "AfricanAmerican": 19210, "Hispanic": 2037, "Other": 1506, "Asian": 641 } },
  admission_type_distribution: { type: "bar", data: { "Emergency": 53940, "Urgent": 18480, "Elective": 18325, "Newborn": 12, "Not Available": 7258 } },
  top_diagnoses: { type: "horizontal_bar", data: { "428": 5765, "414": 4518, "786": 3248, "250": 3102, "427": 2963, "410": 2507, "276": 2400, "496": 2325, "491": 1843, "486": 1735 } },
};

interface DashboardProps {
  type: string;
}

export default function Dashboard({ type }: DashboardProps) {
  const { token } = useAuth();
  const [data, setData] = useState<any>(null);
  const [kpis, setKpis] = useState<any>(DEMO_KPIS);
  const [charts, setCharts] = useState<any>(DEMO_CHARTS);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [type, token]);

  const loadData = async () => {
    setLoading(true);
    try {
      if (token) {
        if (type === "dashboard") {
          const [kpiData, dashData] = await Promise.all([
            analyticsAPI.getKPIs(token),
            analyticsAPI.getDashboard("executive_dashboard", token),
          ]);
          setKpis(kpiData);
          setCharts(dashData.charts || DEMO_CHARTS);
        } else {
          const dashData = await analyticsAPI.getDashboard(`${type}_dashboard`, token);
          setData(dashData);
        }
      }
    } catch (err) {
      console.log("Using demo data (backend not connected)");
    } finally {
      setLoading(false);
    }
  };

  const LoadingSkeleton = () => (
    <div className="space-y-6 animate-pulse">
      <div className="h-8 bg-white/5 rounded-lg w-64"></div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="glass-card p-5 h-32"></div>
        ))}
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {[1, 2].map((i) => (
          <div key={i} className="glass-card p-6 h-80"></div>
        ))}
      </div>
    </div>
  );

  if (loading) {
    return <LoadingSkeleton />;
  }

  if (type === "dashboard") {
    return (
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Executive Dashboard</h1>
            <p className="text-slate-400 text-sm mt-1">Medical KPIs & Analytics Overview</p>
          </div>
          <div className="flex items-center gap-2 text-xs text-emerald-400 glass-card px-3 py-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500 pulse-glow" />
            Live Data
          </div>
        </div>

        {/* KPI Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <KPICard title="Total Encounters" value={kpis.total_encounters} icon="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" color="blue" />
          <KPICard title="Unique Patients" value={kpis.unique_patients} icon="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" color="emerald" />
          <KPICard title="30-Day Readmission" value={`${kpis.readmission_rate_30day}%`} subtitle="Of all encounters" icon="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" color="rose" />
          <KPICard title="Avg Stay (days)" value={kpis.avg_time_in_hospital} subtitle="Per encounter" icon="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" color="amber" />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <KPICard title="Avg Medications" value={kpis.avg_num_medications?.toFixed(1)} icon="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" color="violet" />
          <KPICard title="Emergency Rate" value={`${kpis.emergency_rate}%`} icon="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" color="rose" />
          <KPICard title="Diabetes Med Rate" value={`${kpis.diabetes_med_rate}%`} icon="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" color="blue" />
          <KPICard title="Insulin Usage" value={`${kpis.insulin_usage_rate}%`} icon="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" color="emerald" />
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ChartCard title="Readmission Distribution" type={charts.readmission_distribution?.type || "donut"} data={charts.readmission_distribution?.data || {}} />
          <ChartCard title="Age Distribution" type={charts.age_distribution?.type || "bar"} data={charts.age_distribution?.data || {}} />
          <ChartCard title="Gender Distribution" type={charts.gender_distribution?.type || "pie"} data={charts.gender_distribution?.data || {}} />
          <ChartCard title="Admission Types" type={charts.admission_type_distribution?.type || "bar"} data={charts.admission_type_distribution?.data || {}} />
          <ChartCard title="Race Distribution" type={charts.race_distribution?.type || "bar"} data={charts.race_distribution?.data || {}} height={250} />
          <ChartCard title="Top 10 Primary Diagnoses (ICD)" type={charts.top_diagnoses?.type || "horizontal_bar"} data={charts.top_diagnoses?.data || {}} height={300} />
        </div>
      </div>
    );
  }

  // Predictive Dashboard
  if (type === "predictive") {
    const pData = data || {
      risk_distribution: { type: "donut", data: { Low: 65432, Medium: 25120, High: 11214 } },
      readmission_by_age: { type: "line", data: { "[0-10)": 8.2, "[10-20)": 9.1, "[20-30)": 10.5, "[30-40)": 11.2, "[40-50)": 11.8, "[50-60)": 12.3, "[60-70)": 12.9, "[70-80)": 13.4, "[80-90)": 14.1, "[90-100)": 14.8 } },
      high_risk_count: 11214,
      medium_risk_count: 25120,
      low_risk_count: 65432,
    };

    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold">Predictive Dashboard</h1>
          <p className="text-slate-400 text-sm mt-1">Risk Assessment & Predictive Analytics</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <KPICard title="High Risk Patients" value={pData.high_risk_count} icon="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" color="rose" />
          <KPICard title="Medium Risk" value={pData.medium_risk_count} icon="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" color="amber" />
          <KPICard title="Low Risk" value={pData.low_risk_count} icon="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" color="emerald" />
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ChartCard title="Risk Distribution" type="donut" data={pData.risk_distribution?.data || {}} />
          <ChartCard title="Readmission Rate by Age Group" type="line" data={pData.readmission_by_age?.data || {}} />
        </div>
      </div>
    );
  }

  // Clinical Dashboard
  if (type === "clinical") {
    const cData = data?.charts || {
      a1c_results: { type: "donut", data: { None: 83827, Norm: 4894, ">7": 5124, ">8": 7921 } },
      insulin_usage: { type: "bar", data: { No: 47188, Steady: 31689, Up: 13583, Down: 9306 } },
      metformin_usage: { type: "bar", data: { No: 61738, Steady: 36629, Up: 1710, Down: 1689 } },
    };

    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold">Clinical Dashboard</h1>
          <p className="text-slate-400 text-sm mt-1">Clinical Outcomes & Treatment Effectiveness</p>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ChartCard title="A1C Test Results" type="donut" data={cData.a1c_results?.data || {}} />
          <ChartCard title="Insulin Usage Pattern" type="bar" data={cData.insulin_usage?.data || {}} />
          <ChartCard title="Metformin Usage Pattern" type="bar" data={cData.metformin_usage?.data || {}} />
        </div>
      </div>
    );
  }

  // Operational Dashboard
  if (type === "operational") {
    const oData = data || {
      alerts: { high_priority_patients: 4231, long_stay_patients: 8956, frequent_readmissions: 2847 },
      charts: {
        stay_distribution: { type: "bar", data: { "1": 14223, "2": 13598, "3": 14892, "4": 12456, "5": 10823, "6": 8925, "7": 6843, "8": 5234, "9": 3876, "10": 2987, "11": 2345, "12": 1876, "13": 1543, "14": 2145 } },
      },
    };

    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold">Operational Dashboard</h1>
          <p className="text-slate-400 text-sm mt-1">Workload, Alerts & Resource Management</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <KPICard title="High Priority Patients" value={oData.alerts?.high_priority_patients || 0} icon="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" color="rose" />
          <KPICard title="Long Stay (>10 days)" value={oData.alerts?.long_stay_patients || 0} icon="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" color="amber" />
          <KPICard title="Frequent Readmissions" value={oData.alerts?.frequent_readmissions || 0} icon="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" color="violet" />
        </div>
        <div className="grid grid-cols-1 gap-6">
          <ChartCard title="Hospital Stay Distribution (Days)" type="bar" data={oData.charts?.stay_distribution?.data || {}} height={350} />
        </div>
      </div>
    );
  }

  return <div className="text-slate-400">Dashboard type not found.</div>;
}

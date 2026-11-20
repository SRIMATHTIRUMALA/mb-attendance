import api from './api';

export const getDashboardSummary = async (targetDate = null) => {
  const params = targetDate ? { target_date: targetDate } : {};
  const res = await api.get('/reports/summary', { params });
  return res.data;
};

export const getDailyReport = async (params = {}) => {
  const res = await api.get('/reports/daily', { params });
  return res.data;
};

export const getWeeklyReport = async (params = {}) => {
  const res = await api.get('/reports/weekly', { params });
  return res.data;
};

export const downloadWeeklyExcel = async (params = {}) => {
  const res = await api.get('/reports/download/excel', {
    params,
    responseType: 'blob',
  });
  const url = window.URL.createObjectURL(new Blob([res.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `MB_Solar_Hub_Weekly_Report_${params.employee_id || 'my'}.xlsx`);
  document.body.appendChild(link);
  link.click();
  link.remove();
};

export const downloadReportPdf = async (params = {}) => {
  const res = await api.get('/reports/download/pdf', {
    params,
    responseType: 'blob',
  });
  const url = window.URL.createObjectURL(new Blob([res.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `MB_Solar_Hub_Report_${params.employee_id || 'my'}.pdf`);
  document.body.appendChild(link);
  link.click();
  link.remove();
};

export const triggerManagementDigest = async (reportType = 'daily') => {
  const res = await api.post(`/reports/trigger-digest?report_type=${reportType}`);
  return res.data;
};

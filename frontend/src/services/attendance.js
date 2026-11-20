import api from './api';

export const getTodayStatus = async () => {
  const res = await api.get('/attendance/today');
  return res.data;
};

export const checkIn = async (timestamp = null) => {
  const payload = timestamp ? { timestamp } : {};
  const res = await api.post('/attendance/check-in', payload);
  return res.data;
};

export const checkOut = async (timestamp = null) => {
  const payload = timestamp ? { timestamp } : {};
  const res = await api.post('/attendance/check-out', payload);
  return res.data;
};

export const lunchOut = async (notes = null, timestamp = null) => {
  const payload = { notes, timestamp };
  const res = await api.post('/lunch/out', payload);
  return res.data;
};

export const lunchIn = async (timestamp = null) => {
  const payload = timestamp ? { timestamp } : {};
  const res = await api.post('/lunch/in', payload);
  return res.data;
};

export const getAttendanceHistory = async (params = {}) => {
  const res = await api.get('/attendance/history', { params });
  return res.data;
};

import api from './api';

export const getDailyWork = async (params = {}) => {
  const res = await api.get('/work', { params });
  return res.data;
};

export const createDailyWork = async (workData) => {
  const res = await api.post('/work', workData);
  return res.data;
};

export const updateDailyWork = async (id, updateData) => {
  const res = await api.patch(`/work/${id}`, updateData);
  return res.data;
};

export const deleteDailyWork = async (id) => {
  const res = await api.delete(`/work/${id}`);
  return res.data;
};

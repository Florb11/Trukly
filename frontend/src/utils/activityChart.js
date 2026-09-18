const dayLabelFormatter = new Intl.DateTimeFormat("es-AR", {
  weekday: "short",
});

const padDatePart = (value) => String(value).padStart(2, "0");

const toDateKey = (date) => {
  const year = date.getFullYear();
  const month = padDatePart(date.getMonth() + 1);
  const day = padDatePart(date.getDate());

  return `${year}-${month}-${day}`;
};

export const getLocalDateKey = (value) => {
  if (!value) return "";

  if (typeof value === "string") {
    const match = value.match(/^\d{4}-\d{2}-\d{2}/);
    if (match) return match[0];
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";

  return toDateKey(date);
};

const addDays = (date, amount) => {
  const nextDate = new Date(date);
  nextDate.setDate(date.getDate() + amount);

  return nextDate;
};

export const getLastSevenDays = (referenceDate = new Date()) => {
  const endDate = new Date(
    referenceDate.getFullYear(),
    referenceDate.getMonth(),
    referenceDate.getDate(),
  );

  return Array.from({ length: 7 }, (_, index) =>
    addDays(endDate, index - 6),
  );
};

export const formatDayLabel = (date) =>
  dayLabelFormatter.format(date).replace(".", "");

export const buildWeeklyActivityFromItems = (
  items,
  getDateValue,
  referenceDate = new Date(),
) => {
  const countsByDay = new Map();

  items.forEach((item) => {
    const key = getLocalDateKey(getDateValue(item));
    if (!key) return;

    countsByDay.set(key, (countsByDay.get(key) || 0) + 1);
  });

  return getLastSevenDays(referenceDate).map((date) => {
    const key = toDateKey(date);

    return {
      label: formatDayLabel(date),
      value: countsByDay.get(key) || 0,
      date: key,
    };
  });
};

export const buildWeeklyActivityFromValues = (
  values,
  referenceDate = new Date(),
) => {
  const safeValues = Array.isArray(values) ? values.slice(-7) : [];
  const paddedValues = [
    ...Array(Math.max(7 - safeValues.length, 0)).fill(0),
    ...safeValues,
  ];

  return getLastSevenDays(referenceDate).map((date, index) => ({
    label: formatDayLabel(date),
    value: Number(paddedValues[index]) || 0,
    date: toDateKey(date),
  }));
};

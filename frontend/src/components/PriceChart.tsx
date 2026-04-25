import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";
import type { PricePoint } from "../api/client";

interface Props {
  data: PricePoint[];
  currency: string;
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString("es-AR", { day: "2-digit", month: "short" });
}

function formatPrice(v: number, currency: string) {
  return currency === "ARS"
    ? `$${v.toLocaleString("es-AR")}`
    : `USD ${v.toFixed(2)}`;
}

export default function PriceChart({ data, currency }: Props) {
  if (!data.length) return <p className="text-slate-500 text-sm">Sin historial de precios aún.</p>;

  const chartData = data.map((p) => ({
    date: formatDate(p.scraped_at),
    price: p.price,
  }));

  return (
    <ResponsiveContainer width="100%" height={220}>
      <AreaChart data={chartData} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
        <defs>
          <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
        <XAxis dataKey="date" tick={{ fill: "#94a3b8", fontSize: 11 }} />
        <YAxis
          tick={{ fill: "#94a3b8", fontSize: 11 }}
          tickFormatter={(v) => formatPrice(v, currency)}
          width={90}
        />
        <Tooltip
          contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 8 }}
          labelStyle={{ color: "#94a3b8" }}
          formatter={(v) => [formatPrice(Number(v), currency), "Precio"]}
        />
        <Area
          type="monotone"
          dataKey="price"
          stroke="#3b82f6"
          strokeWidth={2}
          fill="url(#priceGradient)"
          dot={{ fill: "#3b82f6", r: 3 }}
          activeDot={{ r: 5 }}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}

export type UserRole = "admin" | "manager" | "salesperson";

export type CurrentUser = {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  store_id: string | null;
};

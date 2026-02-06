import { Navigate, Outlet } from "react-router"
import { useFrontendSettings } from "../hooks/useFrontendSettings"

export const FeatureFlagRoute = ({ name }: { name: string }) => {
  const {
    settings: { feature_flags, user },
    loading,
  } = useFrontendSettings()

  // NOTE:  (@abachman-dsac) we normally wouldn't check whether frontend settings
  // have loaded, but this component ends with a redirect, which
  // means there is no second chance to check a feature flag if the
  // settings have not yet properly loaded
  if (loading) return null

  if (feature_flags?.[name]) {
    return <Outlet />
  }

  console.warn(
    "route is not available",
    JSON.stringify({ user, feature_flags }),
  )
  return <Navigate to="/" replace />
}

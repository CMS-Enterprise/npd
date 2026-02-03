import { FrontendSettingsContext } from "../src/state/FrontendSettingsProvider"
import { DEFAULT_FRONTEND_SETTINGS } from "./fixtures"

type TestProviderProps = {
  children: React.ReactNode
  settings?: Partial<FrontendSettings>
}

export const TestFrontendSettingsProvider = ({
  children,
  settings,
}: TestProviderProps) => {
  const testSettings = {
    ...DEFAULT_FRONTEND_SETTINGS,
    ...settings,
  }

  const value = {
    settings: testSettings,
    loading: false,
    error: null,
    refetch: () => {},
  }

  return (
    <FrontendSettingsContext.Provider value={value}>
      {children}
    </FrontendSettingsContext.Provider>
  )
}

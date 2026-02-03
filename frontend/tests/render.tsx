import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import {
  render as originalRender,
  type RenderOptions,
} from "@testing-library/react"
import { TestFrontendSettingsProvider } from "./TestFrontendSettingsProvider"

const testQueryClient = new QueryClient()

type CustomRenderOptions = RenderOptions & {
  settings?: Partial<FrontendSettings>
}

export const customRender = (
  ui: React.ReactNode,
  options?: CustomRenderOptions,
) => {
  const { settings, ...renderOptions } = options ?? {}

  return originalRender(
    <QueryClientProvider client={testQueryClient}>
      <TestFrontendSettingsProvider settings={settings}>
        {ui}
      </TestFrontendSettingsProvider>
    </QueryClientProvider>,
    renderOptions,
  )
}

// eslint-disable-next-line react-refresh/only-export-components
export * from "@testing-library/react" // Re-export all original exports
export { customRender as render } // Export the custom render as 'render'

import { Button } from "@cmsgov/design-system"
import React from "react"
import { Footer } from "./Footer"
import { Header } from "./Header"

import classNames from "classnames"
import layout from "../pages/Layout.module.css"

interface ErrorFallbackProps {
  error: Error
  resetErrorBoundary?: () => void
}

// a basic, totally unwrapped error reporting page
export const ErrorFallback: React.FC<ErrorFallbackProps> = ({
  error,
  resetErrorBoundary,
}) => {
  const eclass = classNames(
    "ds-u-fill--accent-primary-lightest",
    "ds-u-padding--2",
    "ds-u-border--1",
    "ds-u-border--error",
    "ds-u-margin-y--7",
  )
  return (
    <>
      <Header />
      <div className={layout.main}>
        <div className="ds-base ds-l-container">
          <div className="ds-l-row">
            <div className="ds-l-lg-col--8 ds-l-md-col--8">
              <div className={layout.spacer}></div>
              <section className={layout.section}>
                <h2>Something went wrong!</h2>

                <div className={eclass}>{error.message}</div>

                {resetErrorBoundary && (
                  <p>
                    <Button onClick={resetErrorBoundary}>Reset page</Button>
                  </p>
                )}
              </section>
            </div>
          </div>
        </div>
      </div>
      <Footer />
    </>
  )
}

interface Props {
  children?: React.ReactNode
  fallback: React.ComponentType<ErrorFallbackProps>
}

interface State {
  hasError: boolean
  error?: Error
  errorInfo?: React.ErrorInfo
}

export class ErrorBoundary extends React.Component<Props, State> {
  public state: State = {
    hasError: false,
  }

  public static getDerivedStateFromError(error: Error): State {
    // Update state so the next render will show the fallback UI.
    return { hasError: true, error }
  }

  public componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error("Uncaught error:", error, errorInfo)
  }

  resetErrorBoundary = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined })
  }

  public render() {
    if (this.state.hasError) {
      const FallbackComponent = this.props.fallback
      return (
        <FallbackComponent
          error={this.state.error!}
          resetErrorBoundary={this.resetErrorBoundary}
        />
      )
    }

    return this.props.children
  }
}

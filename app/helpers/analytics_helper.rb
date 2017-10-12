module AnalyticsHelper
  def google_analytics_tag
    if Rails.env.production?
      render "layouts/analytics/google_analytics_tag", tracking_id: google_tracking_id
    end
  end

  private

  def google_tracking_id
    Rails.application.secrets.analytics["google_tracking_id"]
  end
end

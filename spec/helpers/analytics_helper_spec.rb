require "rails_helper"

RSpec.describe AnalyticsHelper, type: :helper do
  describe "#google_tag_manager" do
    subject { helper.google_analytics_tag }

    context "when environment is not production" do
      before { allow(Rails.env).to receive(:production?).and_return(false) }

      it { is_expected.to be_blank }
    end

    context "when environment is production" do
      before { allow(Rails.env).to receive(:production?).and_return(true) }

      it { is_expected.to include("googletagmanager", "gtag", "<script>") }
    end
  end
end

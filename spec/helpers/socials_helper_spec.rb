require "rails_helper"

RSpec.describe SocialsHelper, type: :helper do
  describe "#facebook_link" do
    subject { helper.facebook_link }

    it "extracts portal facebook portal link from secrets" do
      is_expected.to have_content("facebook.com")
    end

    context "when there is no facebook link in secrets" do
      before { allow(Rails.application.secrets).to receive(:socials).and_return({}) }

      it "raises error"  do
        expect { subject }.to raise_error(KeyError)
      end
    end
  end

  RSpec.describe SocialsHelper, type: :helper do
    describe "#android_link" do
      subject { helper.android_link }

      it "extracts portal android portal link from secrets" do
        is_expected.to have_content("play.google.com")
      end

      context "when there is no android link in secrets" do
        before { allow(Rails.application.secrets).to receive(:socials).and_return({}) }

        it "raises error"  do
          expect { subject }.to raise_error(KeyError)
        end
      end
    end

  describe "#twitter_link" do
    subject { helper.twitter_link }

    it "extracts portal twitter profile link from secrets" do
      is_expected.to have_content("twitter.com")
    end

    context "when there is no twitter link in secrets" do
      before { allow(Rails.application.secrets).to receive(:socials).and_return({}) }

      it "raises error"  do
        expect { subject }.to raise_error(KeyError)
      end
    end
  end
end

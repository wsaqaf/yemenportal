require "rails_helper"

RSpec.describe SourceProposalMailer do
  describe ".notification" do
    subject do
      described_class
        .notification(admin: admin, source: source, submitter_email: submitter_email)
        .deliver_now
    end

    let(:admin) { create(:user) }
    let(:source) { create(:source) }
    let(:submitter_email) { "test@email.com" }

    it "sends an email" do
      expect { subject }.to change { ActionMailer::Base.deliveries.count }.by(1)
    end

    it "sends it to admin" do
      expect(subject.to).to eq([admin.email])
    end

    it "has html part" do
      expect(subject.html_part.body.encoded).to be_present
    end

    it "has text part" do
      expect(subject.text_part.body.encoded).to be_present
    end
  end
end

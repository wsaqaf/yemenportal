require "rails_helper"

RSpec.describe SourceProposalMailer do
  describe ".notification" do
    subject do
      described_class
        .notification(source: source, submitter_email: submitter_email)
        .deliver_now
    end

    let(:submitter_email) { Faker::Internet.email }
    let(:source) { create(:source) }
    let!(:admin) { create(:user, role: "ADMIN") }
    let!(:moderator) { create(:user, role: "MODERATOR") }

    it "sends an email" do
      expect { subject }.to change { ActionMailer::Base.deliveries.count }.by(1)
    end

    it "sends it to admins" do
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

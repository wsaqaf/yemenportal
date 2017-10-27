require "rails_helper"

describe Posts::Flagging::RateApplier do
  describe "#add_rate" do
    subject { described_class.new(post).add_rate(rate) }

    let(:post) { create(:post) }
    let(:rate) { 1 }

    it "increases post rating by passing rate value" do
      expect { subject }.to change { post.review_rating }.from(0).to(rate)
    end
  end

  describe "#subtract_rate" do
    subject { described_class.new(post).subtract_rate(rate) }

    let(:rate) { 1 }
    let(:post) { create(:post, review_rating: rate) }

    it "decreses post rating by passing rate value" do
      expect { subject }.to change { post.review_rating }.from(rate).to(0)
    end
  end
end

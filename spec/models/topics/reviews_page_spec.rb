require "rails_helper"

describe Topics::ReviewsPage do
  let(:user) { instance_double(User) }
  let(:topic) { instance_double(Topic) }
  let(:reviews_page) { described_class.new(user, topic) }

  describe "#topic" do
    it "returns topic passed to constructor" do
      expect(reviews_page.topic).to eq(topic)
    end
  end

  describe "#flags" do
    it "fetches appropriate list of flags" do
      flag_class = class_double(Flag).as_stubbed_const
      review_class = class_double(Review).as_stubbed_const
      allow(flag_class).to receive(:all).and_return(flag_class)
      allow(flag_class).to receive(:include_number_of_reviews_for_topic).and_return([double])
      allow(review_class).to receive(:where).and_return([double(flag: double)])

      expect(flag_class).to receive(:include_number_of_reviews_for_topic).with(topic)
      expect(review_class).to receive(:where).with(moderator: user, topic: topic)

      reviews_page.flags
    end
  end
end

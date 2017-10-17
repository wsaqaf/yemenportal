require "rails_helper"

describe Posts::ReviewsPage do
  let(:user) { instance_double(User) }
  let(:post) { instance_double(Post) }
  let(:reviews_page) { described_class.new(user, post) }

  describe "#post" do
    it "returns post passed to constructor" do
      expect(reviews_page.post).to eq(post)
    end
  end

  describe "#flags" do
    it "fetches appropriate list of flags" do
      flag_class = class_double(Flag).as_stubbed_const
      review_class = class_double(Review).as_stubbed_const
      allow(flag_class).to receive(:all).and_return(flag_class)
      allow(flag_class).to receive(:include_number_of_reviews_for_post).and_return([double])
      allow(review_class).to receive(:where).and_return([double(flag: double)])

      expect(flag_class).to receive(:include_number_of_reviews_for_post).with(post)
      expect(review_class).to receive(:where).with(moderator: user, post: post)

      reviews_page.flags
    end
  end
end

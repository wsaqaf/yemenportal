require "rails_helper"

describe Review do
  describe ".with_resolve_flag" do
    let(:moderator) { create(:user_moderator) }
    let(:post) { create(:post) }

    it "returns empty array if there is no review with resolve flag" do
      flag = create(:flag)
      Review.create(moderator: moderator, post: post, flag: flag)

      expect(Review.with_resolve_flag(post, moderator)).to be_empty
    end

    it "returns an array with one review with resolve flag" do
      flag = create(:resolve_flag)
      review = Review.create(moderator: moderator, post: post, flag: flag)

      expect(Review.with_resolve_flag(post, moderator)).to include(review)
    end
  end

  describe ".reviews_rate" do
    subject { described_class.reviews_rate }

    let(:good_flag) { create(:flag, rate: 1) }
    let(:bad_flag) { create(:flag, rate: -1) }
    let(:review) { create(:review, flag: good_flag) }
    let(:another_review) { create(:review, flag: bad_flag) }
    let(:reviews_rate) { review.flag.rate + another_review.flag.rate }

    it "summarize rating for reviews" do
      is_expected.to eq(reviews_rate)
    end
  end
end

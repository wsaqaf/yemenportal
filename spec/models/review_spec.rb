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

  describe "#add_rating" do
    let(:post) { create(:post) }
    let(:flag) { create(:flag) }
    let(:apply_review) { create(:review, post: post, flag: flag) }

    it "increases post rating by review flag rate" do
      expect { apply_review }.to change { post.review_rating }.from(0).to(flag.rate)
    end
  end

  describe "#subtract_rating" do
    let(:post) { create(:post) }
    let(:flag) { create(:flag) }
    let!(:review) { create(:review, post: post, flag: flag) }
    let(:destroy_review) { review.destroy }

    it "decreses post rating by review flag rate" do
      expect { destroy_review }.to change { post.review_rating }.from(flag.rate).to(0)
    end
  end
end

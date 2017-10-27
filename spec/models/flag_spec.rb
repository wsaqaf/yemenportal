require "rails_helper"

describe Flag do
  describe ".include_number_of_reviews_for_post" do
    it "adds number_of_reviews_for_posr with correct value to Flag instances" do
      user = create(:user)
      post = create(:post)
      another_post = create(:post)
      flag = Flag.create
      Review.create(moderator: user, post: post, flag: flag)
      Review.create(moderator: user, post: another_post, flag: flag)

      flags = Flag.include_number_of_reviews_for_post(post)

      expect(flags.first.number_of_reviews_for_post).to eq(1)
    end
  end

  describe ".reviewed_flags" do
    subject { described_class.reviewed_flags(post) }

    let(:post) { create(:post) }

    context "when there are no review for the post" do
      it "returns no flags for the post" do
        is_expected.to be_empty
      end
    end

    context "when there are some reviews for the post" do
      let(:review) { create(:review, post: post) }
      let!(:flag) { review.flag }

      it "returns flag for review" do
        is_expected.to match([flag])
      end
    end
  end

  describe "#number_of_reviews_for_post" do
    it "equals 0 when post is not specified" do
      expect(Flag.new.number_of_reviews_for_post).to eq(0)
    end
  end
end

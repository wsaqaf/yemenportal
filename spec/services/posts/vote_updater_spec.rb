require "rails_helper"

describe Posts::VoteUpdater do
  let(:user) { instance_double(User) }
  let(:post) { instance_double(Post) }
  let(:updater) { Posts::VoteUpdater.new(user, post) }

  describe "#upvote" do
    shared_examples "post result updater" do
      it "updates voting result of the post" do
        expect(post).to receive(:update_voting_result).with(42)

        updater.upvote
      end
    end

    let(:vote_class) { class_double(Vote).as_stubbed_const }

    context "when post wasn't voted" do
      before do
        allow(vote_class).to receive(:find_by).with(user: user, post: post).and_return(nil)
        allow(vote_class).to receive(:voting_result_for).with(post).and_return(42)
        allow(vote_class).to receive(:create_upvote).with(user: user, post: post)
        allow(post).to receive(:update_voting_result)
      end

      it "creates new Vote instance" do
        expect(vote_class).to receive(:create_upvote).with(user: user, post: post)

        updater.upvote
      end

      it_behaves_like "post result updater"
    end

    context "when post was already downvoted" do
      let(:vote) { instance_double(Vote) }

      before do
        allow(vote_class).to receive(:find_by).with(user: user, post: post).and_return(vote)
        allow(vote_class).to receive(:voting_result_for).with(post).and_return(42)
        allow(vote).to receive(:make_upvote)
        allow(post).to receive(:update_voting_result)
      end

      it "changes value of appropriate Vote instance" do
        expect(vote).to receive(:make_upvote)

        updater.upvote
      end

      it_behaves_like "post result updater"
    end
  end

  describe "#downvote" do
    shared_examples "post result updater" do
      it "updates voting result of the post" do
        expect(post).to receive(:update_voting_result).with(42)

        updater.downvote
      end
    end

    let(:vote_class) { class_double(Vote).as_stubbed_const }

    context "when post wasn't voted" do
      before do
        allow(vote_class).to receive(:find_by).with(user: user, post: post).and_return(nil)
        allow(vote_class).to receive(:voting_result_for).and_return(42)
        allow(vote_class).to receive(:create_downvote)
        allow(post).to receive(:update_voting_result)
      end

      it "creates new Vote instance" do
        expect(vote_class).to receive(:create_downvote).with(user: user, post: post)

        updater.downvote
      end

      it_behaves_like "post result updater"
    end

    context "when post was already upvoted" do
      let(:vote) { instance_double(Vote) }

      before do
        allow(vote_class).to receive(:find_by).with(user: user, post: post).and_return(vote)
        allow(vote_class).to receive(:voting_result_for).and_return(42)
        allow(vote).to receive(:make_downvote)
        allow(post).to receive(:update_voting_result)
      end

      it "changes value of appropriate Vote instance" do
        expect(vote).to receive(:make_downvote)

        updater.downvote
      end

      it_behaves_like "post result updater"
    end
  end

  describe "#delete" do
    let(:vote_class) { class_double(Vote).as_stubbed_const }
    let(:vote) { instance_double(Vote) }

    before do
      allow(vote_class).to receive(:find_by).with(user: user, post: post).and_return(vote)
      allow(vote_class).to receive(:voting_result_for).and_return(42)
      allow(vote).to receive(:destroy)
      allow(post).to receive(:update_voting_result)
    end

    it "removes instance of Vote" do
      expect(vote).to receive(:destroy)

      updater.delete
    end

    it "updates voting result of the post" do
      expect(post).to receive(:update_voting_result).with(42)

      updater.delete
    end
  end
end

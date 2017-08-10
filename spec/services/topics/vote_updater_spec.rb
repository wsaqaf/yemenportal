require "rails_helper"

describe Topics::VoteUpdater do
  let(:user) { instance_double(User) }
  let(:topic) { instance_double(Topic) }
  let(:updater) { Topics::VoteUpdater.new(user, topic) }

  describe "#upvote" do
    shared_examples "topic result updater" do
      it "updates voting result of the topic" do
        expect(topic).to receive(:update_voting_result).with(42)

        updater.upvote
      end
    end

    let(:vote_class) { class_double(Vote).as_stubbed_const }

    context "when post wasn't voted" do
      before do
        allow(vote_class).to receive(:find_by).with(user: user, topic: topic).and_return(nil)
        allow(vote_class).to receive(:voting_result_for).with(topic).and_return(42)
        allow(vote_class).to receive(:create_upvote).with(user: user, topic: topic)
        allow(topic).to receive(:update_voting_result)
      end

      it "creates new Vote instance" do
        expect(vote_class).to receive(:create_upvote).with(user: user, topic: topic)

        updater.upvote
      end

      it_behaves_like "topic result updater"
    end

    context "when post was already downvoted" do
      let(:vote) { instance_double(Vote) }

      before do
        allow(vote_class).to receive(:find_by).with(user: user, topic: topic).and_return(vote)
        allow(vote_class).to receive(:voting_result_for).with(topic).and_return(42)
        allow(vote).to receive(:make_upvote)
        allow(topic).to receive(:update_voting_result)
      end

      it "changes value of appropriate Vote instance" do
        expect(vote).to receive(:make_upvote)

        updater.upvote
      end

      it_behaves_like "topic result updater"
    end
  end

  describe "#downvote" do
    shared_examples "topic result updater" do
      it "updates voting result of the topic" do
        expect(topic).to receive(:update_voting_result).with(42)

        updater.downvote
      end
    end

    let(:vote_class) { class_double(Vote).as_stubbed_const }

    context "when post wasn't voted" do
      before do
        allow(vote_class).to receive(:find_by).with(user: user, topic: topic).and_return(nil)
        allow(vote_class).to receive(:voting_result_for).and_return(42)
        allow(vote_class).to receive(:create_downvote)
        allow(topic).to receive(:update_voting_result)
      end

      it "creates new Vote instance" do
        expect(vote_class).to receive(:create_downvote).with(user: user, topic: topic)

        updater.downvote
      end

      it_behaves_like "topic result updater"
    end

    context "when post was already upvoted" do
      let(:vote) { instance_double(Vote) }

      before do
        allow(vote_class).to receive(:find_by).with(user: user, topic: topic).and_return(vote)
        allow(vote_class).to receive(:voting_result_for).and_return(42)
        allow(vote).to receive(:make_downvote)
        allow(topic).to receive(:update_voting_result)
      end

      it "changes value of appropriate Vote instance" do
        expect(vote).to receive(:make_downvote)

        updater.downvote
      end

      it_behaves_like "topic result updater"
    end
  end

  describe "#delete" do
    let(:vote_class) { class_double(Vote).as_stubbed_const }
    let(:vote) { instance_double(Vote) }

    before do
      allow(vote_class).to receive(:find_by).with(user: user, topic: topic).and_return(vote)
      allow(vote_class).to receive(:voting_result_for).and_return(42)
      allow(vote).to receive(:destroy)
      allow(topic).to receive(:update_voting_result)
    end

    it "removes instance of Vote" do
      expect(vote).to receive(:destroy)

      updater.delete
    end

    it "updates voting result of the topic" do
      expect(topic).to receive(:update_voting_result).with(42)

      updater.delete
    end
  end
end

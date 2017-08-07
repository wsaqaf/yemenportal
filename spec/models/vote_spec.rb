require "rails_helper"

describe Vote do
  context "class methods" do
    let(:user) { instance_double("User") }
    let(:topic) { instance_double("Topic") }

    describe ".create_upvote" do
      it "creates Vote with value equal to 1" do
        expect(Vote).to receive(:create).with(user: user, topic: topic, value: 1)

        Vote.create_upvote(user: user, topic: topic)
      end
    end

    describe ".create_downvote" do
      it "creates Vote with value equal to -1" do
        expect(Vote).to receive(:create).with(user: user, topic: topic, value: -1)

        Vote.create_downvote(user: user, topic: topic)
      end
    end

    describe ".voting_result_for" do
      it "returns sum of values for the topic" do
        expect(Vote).to receive(:where).with(topic: topic).and_return(Vote)
        expect(Vote).to receive(:sum).with(:value).and_return(42)

        expect(Vote.voting_result_for(topic)).to eq(42)
      end
    end
  end

  describe "#make_upvote" do
    it "changes value to 1" do
      vote = Vote.new

      expect(vote).to receive(:update).with(value: 1)

      vote.make_upvote
    end
  end

  describe "#make_downvote" do
    it "changes value to -1" do
      vote = Vote.new

      expect(vote).to receive(:update).with(value: -1)

      vote.make_downvote
    end
  end
end

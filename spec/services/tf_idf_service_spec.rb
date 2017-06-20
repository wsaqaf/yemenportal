require "rails_helper"

describe TfIdfService do
  subject(:service_1) { described_class.new(description: "one two, xt") }
  subject(:service_2) { described_class.new(description: "opa tata a") }

  let(:post) { build :post, id: 1, topic: nil, created_at: Time.now, description: "one two" }
  let(:saved_topic) { build :topic }
  let(:post_2) { build :post, id: 2, topic: saved_topic, created_at: (Time.now - 2.hours), description: "opa tata" }
  let(:posts) { [post, post_2] }

  describe "#post_topic" do
    let(:topic) { double :topic }

    it "create post topic" do
      allow(Post).to receive(:where).and_return(posts)
      allow(Topic).to receive(:create).with(posts: [post]).and_return(topic)

      expect(service_1.post_topic).to eql(topic)
    end

    it "find post topic" do
      allow(Post).to receive(:where).and_return(posts)

      expect(service_2.post_topic).to eql(post_2.topic)
    end

    it "return nil if dont find matcers" do
      allow(Post).to receive(:where).and_return([])

      expect(service_2.post_topic).to be(nil)
    end
  end
end

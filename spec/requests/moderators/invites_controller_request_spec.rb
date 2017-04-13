require "rails_helper"

describe Moderators::InvitesController, type: :request do
  let(:user) { build(:user, role: "moderator", id: "1") }

  describe "#create" do
    let(:do_request) { post "/moderators/#{user.id}/invites", headers: { "HTTP_REFERER" => "some_path" } }

    it "redirect to sources list" do
      allow(User).to receive(:find).with("1").and_return(user)
      expect(user).to receive(:invite!)
      sign_in user
      do_request

      expect(response).to redirect_to("some_path")
    end
  end
end

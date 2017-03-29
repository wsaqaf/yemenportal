require "rails_helper"

describe Users::InvitationsController, type: :request do
  let(:user) { build :user }

  describe "#failure" do
    let(:aaa) { { "user" => { email: "aa@ss.dd" } } }
    let(:do_request) { post user_invitation_path, params: aaa }

    it "redirect to sources list" do
      sign_in user
      allow(User).to receive(:invite!).and_return(user)
      do_request

      expect(response.status).to eq 302
      expect(response).to redirect_to(moderators_path)
    end
  end
end
